import logging

from prometheus_client import Metric
import pytest

from disk_usage_exporter.constants import METRIC_NAME, METRIC_DESCRIPTION


@pytest.fixture
def sample_logger() -> logging.Logger:
    logger = logging.Logger(__name__)
    logger.setLevel(logging.NOTSET)
    return logger


@pytest.fixture
def du_output() -> str:
    return "12      /data"


@pytest.fixture
def sample_metric() -> Metric:
    metric = Metric(METRIC_NAME, METRIC_DESCRIPTION, "gauge")
    metric.add_sample(
        METRIC_NAME,
        {"path": "/data"},
        15.0
    )
    return metric
