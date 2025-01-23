import argparse
import logging
import os
import sys
from typing import Dict, Tuple

from prometheus_client import start_http_server, Gauge
import sh


def process_directories(search_root: str, metric: Gauge, label_name: str):
    for dirpath, dirnames, filenames in os.walk(search_root):
        for dirname in dirnames:
            dirname = os.path.join(args.search_root, dirname)

            label_value, value = get_dir_stat(dirname)
            if label_value == "" or value == "":
                continue

            set_metric(metric, label_name, label_value, value)


def parse_output(raw_data: str) -> Dict[str, str]:
    size, directory = raw_data.split()

    logger.debug(f"Directory: {directory}")
    logger.debug(f"Size: {size}")

    return {
        "directory": directory,
        "size": size
    }


def get_dir_stat(dirname: str) -> Tuple[str, str]:
    dir_stat = sh.du("-s", dirname, _ok_code=[0, 1])

    logger.info(dir_stat[:-1])

    parsed_output = parse_output(dir_stat)
    if parsed_output:
        return parsed_output["directory"], parsed_output["size"]
    return "", ""


def set_metric(metric: Gauge, label_name: str, label_value: str, value: str):
    metric.labels(
        **{label_name: label_value}
    ).set(float(value))


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
    parser.add_argument("--port", action="store", type=int, default="8100", required=False, help="")
    parser.add_argument("--search-root", action="store", type=str, default="/", required=False, help="")
    parser.add_argument("--max-depth", action="store", type=int, default=1, required=False, help="")
    parser.add_argument("-d", "--debug", action="store_const", const=logging.DEBUG,
                        dest="loglevel", default=logging.INFO, required=False, help="")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logger = get_logger(args.loglevel)

    label = "path"
    disk_usage = Gauge("directory_disk_usage", "Directory size", [label])

    start_http_server(args.port)
    try:
        while True:
            process_directories(args.search_root, disk_usage, label)
    except Exception as e:
        logger.error(e)
