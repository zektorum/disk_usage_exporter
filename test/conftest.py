import logging
import os
import random
import shutil
from typing import Dict, List

from prometheus_client import CollectorRegistry, Gauge, Metric
import pytest
import sh

from disk_usage_exporter.constants import METRIC_NAME, METRIC_DESCRIPTION, METRIC_LABEL_NAME


def add_value_to_metric(metric: Metric, raw_value: Dict[str, str]):
    metric.add_sample(
        METRIC_NAME,
        {METRIC_LABEL_NAME: raw_value["path"]},
        float(raw_value["size"])
    )


@pytest.fixture
def empty_metric() -> Metric:
    return Metric(METRIC_NAME, METRIC_DESCRIPTION, "gauge")


@pytest.fixture
def empty_gauge_metric() -> Gauge:
    registry = CollectorRegistry()
    return Gauge(METRIC_NAME, METRIC_DESCRIPTION, [METRIC_LABEL_NAME], registry=registry)


@pytest.fixture
def raw_values() -> List[Dict[str, str]]:
    return [
        {"path": "/data",  "size": "15"},
        {"path": "/opt",   "size": "494988"},
        {"path": "/run",   "size": "3780"},
        {"path": "/tmp",   "size": "40"},
        {"path": "/media", "size": "8"},
        {"path": "/dev",   "size": "260"}
    ]


@pytest.fixture
def metric_with_multiple_labels(empty_metric: Metric, raw_values: List[Dict[str, str]]) -> Metric:
    metric = empty_metric
    for value in raw_values:
        add_value_to_metric(metric, value)
    return metric


@pytest.fixture
def sample_logger() -> logging.Logger:
    logger = logging.Logger(__name__)
    logger.setLevel(logging.NOTSET)
    return logger


@pytest.fixture
def du_output() -> str:
    return "12      /data"


@pytest.fixture
def sample_metric(empty_metric: Metric) -> Metric:
    metric = empty_metric
    metric.add_sample(
        METRIC_NAME,
        {"path": "/data"},
        15.0
    )
    return metric


@pytest.fixture
def sample_directory_structure_with_data(request: pytest.FixtureRequest) -> List[Dict[str, str]]:
    root_name = "root"
    root_path = os.path.join(os.getcwd(), root_name)
    os.mkdir(root_path)
    dirs = ["data", "opt", "media", "run"]
    values = []
    for dir_name in dirs:
        path = os.path.join(root_path, dir_name)
        path_to_file = os.path.join(path, "file")
        size = random.randint(0, 10000)

        os.mkdir(path)
        with open(path_to_file, "wb") as file:
            file.write(b"0" * size)
        dir_size = sh.du(path, _ok_code=[0, 1]).split()[0]

        values.append({"directory": path, "size": dir_size})

    def cleanup():
        shutil.rmtree(root_path)

    request.addfinalizer(cleanup)
    return values
