import disk_usage_exporter.const as const
from disk_usage_exporter.disk_usage_exporter import parse_output


class TestDuOutputParser:
    @staticmethod
    def test_empty_output(incorrect_raw_data: str):
        output = parse_output(incorrect_raw_data)
        assert output["directory"] == const.INCORRECT_DIR_NAME and output["size"] == const.INCORRECT_DIR_SIZE

    @staticmethod
    def test_full_output(du_output: str):
        raw_data = du_output
        output = parse_output(raw_data)
        assert output["directory"] == "/data" and output["size"] == "12"
