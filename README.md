[![Python application](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml/badge.svg)](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml)

# GEMINI: CCSR mapping code (beta version)

The code in this repository maps diagnosis codes from International Classification of Diseases 10th Revision (ICD10) codes to Clinical Classifications Software Refined (CCSR) categories. For more details, please refer to this paper [Malecki et al. (2022)](LINK)

Note: The current release is a beta version and is subject to change. 

## Installation & set-up

Please download/clone the repository to a local directory. 

Check `run_example.py` for an example of how to map a list of ICD-10 diagnosis codes (see `example_codes_to_map.csv`) to CCSR categories. Please see the documentation for a description of the four dataframes returned by the main function `map_icd_to_ccsr`.  

By default, the code will map ICD-10 diagnosis codes to CCSR version v2020-3. To change the CCSR version, please download the latest CCSR categorization file from the [CCSR website](https://www.hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp). Please make sure that the CCSR file has been formatted to match the description found in the [documentation](https://github.com/GEMINI-Medicine/gemini-ccsr/blob/master/docs/build/html/index.html) (also see `example_ccsr_v2020-3.csv` for an example of a correctly formatted CCSR file). 

## Usage

These are the essential lines of codes required to map a list of ICD-10 codes:

```python
import pandas as pd
from gemini_ccsr.main import map_icd_to_ccsr

# ICD codes that should be mapped
icd = ['A000', 'A001', 'A0101', 'A085']
# Official CCSR categorization file
ccsr = pd.read_csv(<ccsr_filepath>)

direct, automatic, semiautomatic, failed = map_icd_to_ccsr(icd, ccsr)
```

## Citation

[Malecki et al. (2022)](LINK)

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Version
Version 1.0 - November 2022
