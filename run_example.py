# -*- coding: utf-8 -*-
"""
@author: loffleraSMH
"""

import pandas as pd
from gemini_ccsr.main import map_icd_to_ccsr


#%% READ FILES
## Official CCSR categorization file (CCSR v2020.3 - formatted file)
ccsr = pd.read_csv('example_ccsr_v2020-3.csv', dtype= 'str')


## List of ICD codes that should be mapped
# provide list...
#icd = ['A020','A021','C440','A010','A022','C44001','A1520','A1521', 'C440', 'C440','C440','E90']

# ... or read .csv file containing ICD codes to be mapped
icd = pd.read_csv('tests/test_data/codes_to_map.csv', dtype= 'str'); 
icd = icd['diagnosis_code'].tolist()

## MAKE SURE ALL INITIAL LETTERS ARE CAPITALIZED
icd = [i.capitalize() for i in icd]


#%% RUN MAPPING ALGORITHM
direct, automatic, semiautomatic, failed = map_icd_to_ccsr(icd, ccsr)
       
# show mapping results
print('\n*** MAPPING RESULTS from ' + str(len(icd)) + ' codes ***')
print('Direct: N = ' + str(len(direct)) + ' (' + str(round(100*len(direct)/len(icd),1)) + '%)')
print('Automatic: N = ' + str(len(automatic)) + ' (' + str(round(100*len(automatic)/len(icd),1)) + '%)')
print('Semi-automatic: N = ' + str(len(semiautomatic['Queried ICD'].unique())) + ' (' + str(round(100*len(semiautomatic)/len(icd),1)) + '%)')
print('Failed: N = ' + str(len(failed)) + ' (' + str(round(100*len(failed)/len(icd),1)) + '%)')
