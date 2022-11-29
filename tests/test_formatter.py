import unittest

import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np

from gemini_ccsr import formatter


class TestFormatter(unittest.TestCase):
    ccsr = pd.read_csv('tests/test_data/clean_ccsr_v2020-3.csv', dtype= 'str')
    ccsr = ccsr.drop(columns=['icd_description'])

    icd = np.array(['A000', 'A001', 'A0101', 'A085'])

    def test_check_ccsr(self):
        assert_frame_equal(
            formatter.check_ccsr(self.ccsr), self.ccsr, 'Should be equal')

    def test_check_icd_numpy(self):
        self.assertEqual(len(formatter.check_icd(self.icd)), len(self.icd))

    def test_check_icd_list(self):
        self.assertEqual(len(formatter.check_icd(self.icd.tolist())),
                          len(self.icd))

    def test_check_icd_ser(self):
        self.assertEqual(len(formatter.check_icd(pd.Series(self.icd))),
                          len(self.icd))

    def test_check_icd_df(self):
        with self.assertRaises(ValueError):
            formatter.check_icd(pd.DataFrame(self.icd))

    # def test_add_default_valid(self):
        
    #     res = formatter.add_default(
    #         self.ccsr.drop(columns=['ccsr_def']).rename(columns={'icd': 'Queried ICD'}), self.ccsr)
    #     res = res[self.ccsr.rename(columns={'icd': 'Queried ICD'}).columns]
        
    #     assert_frame_equal(res, self.ccsr.rename(columns={'icd': 'Queried ICD'}))

    # def test_add_default_overwrite(self):
    #     changed = self.ccsr.copy()
    #     changed['ccsr_def'] = 'wrong categories'
    #     res = formatter.add_default(changed.rename(columns={'icd': 'Queried ICD'}), self.ccsr)
    #     assert_frame_equal(res, self.ccsr.rename(columns={'icd': 'Queried ICD'}))

    def test_add_default_empty(self):
        res = formatter.add_default(
            pd.DataFrame(columns=self.ccsr.drop(columns=['ccsr_def']).rename(columns={'icd': 'Queried ICD'}).columns), self.ccsr)
        self.assertEqual(len(res), 0)

    def test_add_descs_valid(self):
        use_cols = [col for col in self.ccsr.columns
                    if not col.endswith('_desc')]
        no_desc_ccsr = self.ccsr[use_cols]
        res = formatter.add_descs(no_desc_ccsr, self.ccsr,True)
        assert_frame_equal(res, self.ccsr)

    def test_add_descs_overwrite(self):
        res = formatter.add_descs(self.ccsr, self.ccsr,True)
        assert_frame_equal(res, self.ccsr)

    def test_add_descs_missing(self):
        with self.assertRaises(ValueError):
            formatter.add_descs(
                self.ccsr.drop(columns=['ccsr_6']), self.ccsr,True)


if __name__ == '__main__':
    unittest.main()
