import argparse
import logging
import sys

import disk_usage_exporter.const as const


def get_logger(loglevel: str) -> logging.Logger:
    """Create logger.

    :param loglevel: one of the following values: logging.INFO or logging.DEBUG
    :return: logger object
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    :return: CLI args
    """
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
