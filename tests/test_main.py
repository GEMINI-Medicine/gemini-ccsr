import unittest

import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np

from gemini_ccsr import main


class TestMain(unittest.TestCase):
    ccsr = pd.read_csv(
        'tests/test_data/ccsr.csv', dtype=str).replace({np.nan: None})
    direct = pd.read_csv(
        'tests/test_data/direct.csv', dtype=str).replace({np.nan: None})
    resolved = pd.read_csv(
        'tests/test_data/resolved.csv', dtype=str).replace({np.nan: None})
    unresolved = pd.read_csv(
        'tests/test_data/unresolved.csv', dtype=str).replace({np.nan: None})
    failed = pd.read_csv(
        'tests/test_data/failed.csv', dtype=str).replace({np.nan: None})
    icd = pd.concat(
        [direct, resolved, unresolved, failed])['Queried ICD'].astype(str)

    def test_map_icd_to_ccsr_verbose(self):
        _ = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=True)

    def test_map_icd_to_ccsr_direct(self):
        direct = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=False)[0]
        assert_frame_equal(direct, self.direct)

    def test_map_icd_to_ccsr_resolved(self):
        resolved = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=False)[1]
        assert_frame_equal(resolved, self.resolved)

    def test_map_icd_to_ccsr_unresolved(self):
        unresolved = main.map_icd_to_ccsr(
            self.icd, self.ccsr, verbose=False)[2]
        assert_frame_equal(unresolved, self.unresolved)

    def test_map_icd_to_ccsr_failed(self):
        failed = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=False)[3]
        assert_frame_equal(failed, self.failed)


if __name__ == '__main__':
    unittest.main()
