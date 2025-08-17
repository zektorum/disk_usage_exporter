import os
from typing import Dict, List

import pytest

from disk_usage_exporter.disk_usage_exporter import get_dir_stat

SEARCH_ROOT = os.path.join(os.getcwd(), "root")


class TestDirStat:
    @pytest.mark.parametrize('sample_directory_structure_with_data', [SEARCH_ROOT], indirect=True)
    def test_dir_size(self, sample_directory_structure_with_data: List[Dict[str, str]]):
        dirs = sample_directory_structure_with_data

        for dir_values in dirs:
            assert dir_values["size"] == get_dir_stat(dir_values["directory"])
