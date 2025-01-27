import logging

import pytest


@pytest.fixture
def get_logger() -> logging.Logger:
    logger = logging.Logger(__name__)
    logger.setLevel(logging.NOTSET)
    return logger


@pytest.fixture
def du_output():
    return "12      /data"
