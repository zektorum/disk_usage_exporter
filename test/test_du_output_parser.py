import logging

import pytest

from conftest import get_logger, du_output
from disk_usage_exporter.disk_usage_exporter import parse_output


@pytest.mark.usefixtures("get_logger")
class TestDuOutputParser:
    @staticmethod
    def test_empty_output(get_logger: logging.Logger):
        raw_data = ""
        logger = get_logger
        output = parse_output(raw_data, logger)
        assert output["directory"] == "" and output["size"] == ""

    @staticmethod
    def test_full_output(du_output: str, get_logger: logging.Logger):
        raw_data = du_output
        logger = get_logger
        output = parse_output(raw_data, logger)
        assert output["directory"] == "/data" and output["size"] == "12"
