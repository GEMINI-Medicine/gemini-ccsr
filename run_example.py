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
# read .csv file containing ICD codes to be mapped...
icd = pd.read_csv('example_codes_to_map.csv', dtype= 'str'); 
icd = icd['diagnosis_code'].tolist()

## ... or provide list of codes here
#icd = ['A001','A081','A1611','C767','E1030','E750','E90','F001','F012','G3109','H04209','I132','N26','O37033','R1958','S917','T86881','Z017','Z507']


#%% RUN MAPPING ALGORITHM
direct, automatic, semiautomatic, failed = map_icd_to_ccsr(icd, ccsr)
       
# show mapping results
print('\n*** MAPPING RESULTS from ' + str(len(icd)) + ' codes ***')
print('Direct: N = ' + str(len(direct)) + ' (' + str(round(100*len(direct)/len(icd),1)) + '%)')
print('Automatic: N = ' + str(len(automatic)) + ' (' + str(round(100*len(automatic)/len(icd),1)) + '%)')
print('Semi-automatic: N = ' + str(len(semiautomatic['queried_icd'].unique())) + ' (' + str(round(100*len(semiautomatic)/len(icd),1)) + '%)')
print('Failed: N = ' + str(len(failed)) + ' (' + str(round(100*len(failed)/len(icd),1)) + '%)')
