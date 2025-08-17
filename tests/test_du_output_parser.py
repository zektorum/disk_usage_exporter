import disk_usage_exporter.const as const
from disk_usage_exporter.disk_usage_exporter import get_size_from_raw_output


class TestDuOutputParser:
    @staticmethod
    def test_empty_output(incorrect_raw_data: str):
        assert get_size_from_raw_output(incorrect_raw_data) == const.INCORRECT_DIR_SIZE

    @staticmethod
    def test_full_output(du_output: str):
        assert get_size_from_raw_output(du_output) == "12"
