import logging
import os
from typing import Dict, Generator, List

from prometheus_client import Gauge
import pytest
import shutil

import disk_usage_exporter.const as const
from disk_usage_exporter.disk_usage_exporter import exclude_dirs, process_directories

SEARCH_ROOT = os.path.join(os.getcwd(), "root")


class TestExcludeDirs:
    directories_list: List[str] = ["/home", "/mnt", "/tmp", "/root"]

    @pytest.mark.parametrize(
        ("dirs_to_exclude", "dirs_to_processing"),
        [
            ([], directories_list),
            (["/home"], [_ for _ in directories_list if _ not in ["/home"]]),
            (["/home", "/mnt"], [_ for _ in directories_list if _ not in ["/home", "/mnt"]]),
            (["/home", "/mnt", "/tmp", "/root"], [_ for _ in directories_list if _ not in ["/home", "/mnt", "/tmp", "/root"]]),
            (["/sdfasdf"], directories_list),
            (["/home", "/mnt", "/tmp", "/root", "/sdfa"], [_ for _ in directories_list if _ not in ["/home", "/mnt", "/tmp", "/root"]]),
            ([""], directories_list)
        ],
        ids=[
            "exclude with no args", "exclude one dir", "exclude two dirs", "exclude all dirs",
            "exclude only non existing dir", "exclude non existing dir together with regular dirs", "exclude empty arg"
        ]
    )
    def test_exclude_dir(self, dirs_to_exclude: List[str], dirs_to_processing: List[str], sample_logger: logging.Logger,
                         monkeypatch: Generator[pytest.MonkeyPatch]):
        monkeypatch.setattr(os, "listdir", lambda path: self.directories_list)
        monkeypatch.setattr(os.path, "isdir", lambda path: True)

        actual = sorted(exclude_dirs("/", dirs_to_exclude, sample_logger))
        expected = sorted(dirs_to_processing)

        assert len(actual) == len(expected)

        for a, b in zip(actual, expected):
            assert a == b


@pytest.mark.skip(reason="need to check what does process_directories return")
class TestProcessingDirectories:
    @pytest.mark.parametrize('simple_directory_structure_with_data', [SEARCH_ROOT])
    def test_processing(self, simple_directory_structure_with_data: List[Dict[str, str]], sample_logger: logging.Logger,
                        empty_gauge_metric: Gauge, request: pytest.FixtureRequest):
        metric = empty_gauge_metric
        os.mkdir(SEARCH_ROOT)
        request.addfinalizer(lambda: shutil.rmtree(SEARCH_ROOT))

        process_directories(
            search_root=SEARCH_ROOT,
            dirs_to_exclude=[],
            metric=metric,
            label_name=const.METRIC_LABEL_NAME,
            logger=sample_logger
        )
        assert metric.collect() == {}
