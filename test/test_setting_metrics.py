from prometheus_client import Gauge, Metric

from disk_usage_exporter.disk_usage_exporter import set_metric
from disk_usage_exporter.constants import METRIC_NAME, METRIC_DESCRIPTION, METRIC_LABEL_NAME


class TestMetricSetting:
    def test_setting(self, sample_metric: Metric):
        path = "/data"
        size = "15"
        metric = Gauge(METRIC_NAME, METRIC_DESCRIPTION, [METRIC_LABEL_NAME])
        set_metric(metric, METRIC_LABEL_NAME, path, size)

        assert metric.collect() == [sample_metric]
