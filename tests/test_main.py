from gemini_ccsr import main

import unittest

import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np
import ast



class TestMain(unittest.TestCase):
    ccsr = pd.read_csv(
        'tests/test_data/clean_ccsr_v2020-3.csv', dtype=str).replace({np.nan: None})
    direct = pd.read_csv(
        'tests/test_data/direct.csv', dtype=str).replace({np.nan: None})
    automatic = pd.read_csv(
        'tests/test_data/automatic.csv', dtype=str).replace({np.nan: None})    
    automatic['Related Codes'] = automatic['Related Codes'].apply(lambda x: ast.literal_eval(x))

    semiautomatic = pd.read_csv(
        'tests/test_data/semiautomatic.csv', dtype={'Prct_fam_agree': float}).replace({np.nan: None})
    
    failed = pd.read_csv(
        'tests/test_data/failed.csv', dtype=str).replace({np.nan: None})
    icd = pd.concat(
        [direct, automatic, semiautomatic, failed])['Queried ICD'].astype(str)

    def test_map_icd_to_ccsr_verbose(self):
        _ = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=True)

    def test_map_icd_to_ccsr_direct(self):
        direct = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=False)[0]
        assert_frame_equal(direct, self.direct)

    def test_map_icd_to_ccsr_automatic(self):
        automatic = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=False)[1]
        assert_frame_equal(automatic, self.automatic)

    def test_map_icd_to_ccsr_semiautomatic(self):
        semiautomatic = main.map_icd_to_ccsr(
            self.icd, self.ccsr, verbose=False)[2]
        assert_frame_equal(semiautomatic, self.semiautomatic)

    def test_map_icd_to_ccsr_failed(self):
        failed = main.map_icd_to_ccsr(self.icd, self.ccsr, verbose=False)[3]
        assert_frame_equal(failed, self.failed)


if __name__ == '__main__':
    unittest.main()
