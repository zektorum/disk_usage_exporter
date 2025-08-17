import logging
import os
import sys
import traceback
from typing import List

import disk_usage_exporter.const as const
from disk_usage_exporter.utils import get_logger, parse_args

from prometheus_client import start_http_server, Gauge
from setproctitle import setproctitle
import sh


def exclude_dirs(search_root: str, dirs_to_exclude: List[str], logger: logging.Logger) -> List[str]:
    """Exclude directories from processing list.

    :param search_root: root path to search
    :param dirs_to_exclude: directories to be excluded from processing
    :param logger: logger object
    :return: ready to processing list of directories
    """
    found_dirs = []
    dirs_to_processing = []
    for file in sorted(os.listdir(search_root)):
        full_path = os.path.join(search_root, file)
        if os.path.isdir(full_path):
            found_dirs.append(full_path)
            if full_path not in dirs_to_exclude:
                dirs_to_processing.append(full_path)

    logger.info(f"Found dirs: {found_dirs}")
    logger.info(f"Dirs to processing: {dirs_to_processing}")

    return dirs_to_processing


def process_directories(
    search_root: str, dirs_to_exclude: List[str], metric: Gauge, label_name: str, logger: logging.Logger
):
    """Calculate directory sizes and set metrics.

    :param search_root: root path to search
    :param dirs_to_exclude: directories to be excluded from processing
    :param metric: metric to be set
    :param label_name: directory size metric name
    :param logger: logger object
    :return: None
    """
    dirs_to_process = exclude_dirs(search_root, dirs_to_exclude, logger)
    for dir_name in dirs_to_process:
        dir_name = os.path.join(search_root, dir_name)

        logger.debug(f"Calculating '{dir_name}' size")
        value = get_dir_stat(dir_name)
        if value == const.INCORRECT_DIR_SIZE:
            continue

        logger.debug(f"{const.METRIC_NAME}{{path=\"{dir_name}\"}}\t\t{float(value)}")
        set_metric(metric, label_name, dir_name, value)


def get_size_from_raw_output(raw_data: str) -> str:
    """Parse the output of `du` and return the directory name with size.

    :param raw_data: `du` output
    :return: dictionary in following format: {'directory': <directory_name>, 'size': <directory_size>}
    """
    if raw_data:
        size, directory = raw_data.split()
    else:
        size, directory = const.INCORRECT_DIR_SIZE, const.INCORRECT_DIR_NAME

    return size


def get_dir_stat(dir_name: str) -> str:
    """Get the size of a directory using `du` from `coreutils` and return the name and size of the directory.

    :param dir_name: name of the directory
    :return: directory name, directory size
    """
    dir_stat = sh.du(const.DU_ARGS, dir_name, _ok_code=const.VALID_DU_EXIT_CODES)

    return get_size_from_raw_output(dir_stat)


def set_metric(metric: Gauge, label_name: str, label_value: str, value: str):
    """Set the label and metric value.

    :param metric: metric object
    :param label_name: name of the label
    :param label_value: the value of the specified label
    :param value: value of the specified metric
    :return: None
    """
    metric.labels(**{label_name: label_value}).set(float(value))


def main():
    """Prometheus exporter for disk usage metrics."""
    setproctitle(const.PROCESS_TITLE)

    args = parse_args()
    logger = get_logger(args.loglevel)

    metric_label = const.METRIC_LABEL_NAME
    disk_usage_metric = Gauge(const.METRIC_NAME, const.METRIC_DESCRIPTION, [metric_label])

    start_http_server(args.port, args.addr)
    logger.info(f"Starting listening {const.METRICS_HOST}:{const.METRICS_PORT}")
    try:
        while True:
            process_directories(args.search_root, args.exclude_dirs, disk_usage_metric, metric_label, logger)
    except Exception as e:
        logger.error(f"Exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
