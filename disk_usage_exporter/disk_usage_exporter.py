import argparse
import logging
import os
import sys
import traceback
from typing import Dict, Tuple

import disk_usage_exporter.const as const

from prometheus_client import start_http_server, Gauge
from setproctitle import setproctitle
import sh


def process_directories(
    search_root: str, metric: Gauge, label_name: str, logger: logging.Logger
):
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
    if raw_data:
        size, directory = raw_data.split()
    else:
        size, directory = const.INCORRECT_DIR_SIZE, const. INCORRECT_DIR_NAME

    return {"directory": directory, "size": size}


def get_dir_stat(dir_name: str) -> Tuple[str, str]:
    dir_stat = sh.du("-s", dir_name, _ok_code=[0, 1])

    parsed_output = parse_output(dir_stat)
    return parsed_output["directory"], parsed_output["size"]


def set_metric(metric: Gauge, label_name: str, label_value: str, value: str):
    metric.labels(**{label_name: label_value}).set(float(value))


def get_logger(loglevel: str) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--addr",
        action="store",
        type=str,
        default=const.METRICS_HOST,
        required=False,
        help="specify metrics host"
    )
    parser.add_argument(
        "--port",
        action="store",
        type=int,
        default=const.METRICS_PORT,
        required=False,
        help="specify metrics port",
    )
    parser.add_argument(
        "--search-root",
        action="store",
        type=str,
        default=const.SEARCH_ROOT,
        required=False,
        help="specify the directory that will be used to search for subdirectories to analyze",
    )
    # parser.add_argument(
    #     "--max-depth",
    #     action="store",
    #     type=int,
    #     default=const.MAX_DEPTH,
    #     required=False,
    #     help="specify max depth of subdirectory search",
    # )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="loglevel",
        default=const.DEFAULT_LOG_LEVEL,
        required=False,
        help="enable debug logs",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        dest="version",
        version="%(prog)s " + const.VERSION
    )
    return parser.parse_args()


def main():
    setproctitle(const.PROCESS_TITLE)

    args = parse_args()
    logger = get_logger(args.loglevel)

    label = const.METRIC_LABEL_NAME
    disk_usage = Gauge(const.METRIC_NAME, const.METRIC_DESCRIPTION, [label])

    start_http_server(args.port, args.addr)
    logger.info(f"Starting listening {const.METRICS_HOST}:{const.METRICS_PORT}")
    try:
        while True:
            process_directories(args.search_root, disk_usage, label, logger)
    except Exception as e:
        logger.error(f"Exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
