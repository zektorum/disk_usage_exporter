import logging
import os
import sys
import traceback
from typing import Dict, Tuple

import disk_usage_exporter.const as const
from disk_usage_exporter.utils import get_logger, parse_args

from prometheus_client import start_http_server, Gauge
from setproctitle import setproctitle
import sh


def process_directories(
    search_root: str, metric: Gauge, label_name: str, logger: logging.Logger
):
    """Calculate directory sizes and set metrics.

    :param search_root: root path to search
    :param metric: metric to be set
    :param label_name: directory size metric name
    :param logger: logger object
    :return: None
    """
    dirs = [
        file for file in os.listdir(search_root) if os.path.isdir(os.path.join(search_root, file))
    ]
    logger.info(f"Found dirs: {dirs}")
    for dir_name in dirs:
        dir_name = os.path.join(search_root, dir_name)

        logger.debug(f"Calculating '{dir_name}' size")
        label_value, value = get_dir_stat(dir_name)
        if label_value == const.INCORRECT_DIR_NAME or value == const.INCORRECT_DIR_SIZE:
            continue

        logger.debug(f"{const.METRIC_NAME}{{path=\"{label_value}\"}}\t\t{float(value)}")
        set_metric(metric, label_name, label_value, value)


def parse_output(raw_data: str) -> Dict[str, str]:
    """Parse the output of `du` and return the directory name with size.

    :param raw_data: `du` output
    :return: dictionary in following format: {'directory': <directory_name>, 'size': <directory_size>}
    """
    if raw_data:
        size, directory = raw_data.split()
    else:
        size, directory = const.INCORRECT_DIR_SIZE, const.INCORRECT_DIR_NAME

    return {"directory": directory, "size": size}


def get_dir_stat(dir_name: str) -> Tuple[str, str]:
    """Get the size of a directory using `du` from `coreutils` and return the name and size of the directory.

    :param dir_name: name of the directory
    :return: directory name, directory size
    """
    dir_stat = sh.du(const.DU_ARGS, dir_name, _ok_code=const.VALID_DU_EXIT_CODES)

    parsed_output = parse_output(dir_stat)
    return parsed_output["directory"], parsed_output["size"]


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
    setproctitle(const.PROCESS_TITLE)

    args = parse_args()
    logger = get_logger(args.loglevel)

    metric_label = const.METRIC_LABEL_NAME
    disk_usage_metric = Gauge(const.METRIC_NAME, const.METRIC_DESCRIPTION, [metric_label])

    start_http_server(args.port, args.addr)
    logger.info(f"Starting listening {const.METRICS_HOST}:{const.METRICS_PORT}")
    try:
        while True:
            process_directories(args.search_root, disk_usage_metric, metric_label, logger)
    except Exception as e:
        logger.error(f"Exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
