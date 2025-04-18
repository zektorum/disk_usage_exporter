import logging

from disk_usage_exporter.release import __version__


DEFAULT_LOG_LEVEL = logging.INFO
PROCESS_TITLE = "disk_usage_exporter"
METRICS_HOST = "127.0.0.1"
METRICS_PORT = "8100"
METRIC_NAME = "disk_usage_by_directories"
METRIC_DESCRIPTION = "Directory size"
METRIC_LABEL_NAME = "path"
DU_ARGS = "-s"
INCORRECT_DIR_NAME = ""
INCORRECT_DIR_SIZE = ""
VALID_DU_EXIT_CODES = [0, 1]
MAX_DEPTH = 1
SEARCH_ROOT = "/"
VERSION = __version__
