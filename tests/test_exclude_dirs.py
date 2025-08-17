import logging
import os
from typing import List

import pytest

from disk_usage_exporter.disk_usage_exporter import exclude_dirs


class TestExcludeDirs:
    directories_list: List[str] = ["/data", "/opt", "/media", "/run"]

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
        ]
    )
    def test_exclude_dir(self, dirs_to_exclude: List[str], dirs_to_processing: List[str], sample_logger: logging.Logger,
                         monkeypatch):
        def mock_listdir(path: str):
            return self.directories_list

        def mock_isdir(path: str):
            return True

        monkeypatch.setattr(os, "listdir", mock_listdir)
        monkeypatch.setattr(os.path, "isdir", mock_isdir)

        actual = sorted(exclude_dirs("/", dirs_to_exclude, sample_logger))
        expected = sorted(dirs_to_processing)

        assert len(actual) == len(expected)

        for a, b in zip(actual, expected):
            assert a == b
