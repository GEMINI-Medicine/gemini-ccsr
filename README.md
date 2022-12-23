[![Python application](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml/badge.svg)](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml)

# GEMINI: CCSR mapping code (beta version)

The code in this repository maps diagnosis codes from International Classification of Diseases 10th Revision (ICD-10) codes to Clinical Classifications Software Refined (CCSR) categories. For more details, please refer to this paper [Malecki et al. (2022). Tools for categorization of diagnostic codes in hospital data: Operationalizing CCSR into a patient data repository.](https://medrxiv.org/cgi/content/short/2022.11.29.22282888v1)

Note: The current release is a beta version and is subject to change. 

## Installation & set-up

Please download or clone the repository to a local directory (`/path/to/gemini-ccsr/`). Run `pip3 install --user /path/to/gemini-ccsr/` to install.

Check `run_example.py` for an example of how to map a list of ICD-10 diagnosis codes (in `example_codes_to_map.csv`) to CCSR categories. Please see the documentation for a description of the four dataframes returned by the main function `map_icd_to_ccsr`. Codes that are returned in the semiautomatic/failed dataframes will need to be carefully reviewed, and may need to be mapped manually (see [here](https://medrxiv.org/cgi/content/short/2022.11.29.22282888v1) for more details). 

## CCSR version

By default, the code will map ICD-10 diagnosis codes to CCSR version v2020-3. To change the CCSR version, please download the latest CCSR categorization file from the [CCSR website](https://www.hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp). Please make sure that the CCSR file has been formatted to match the description found in the [documentation](https://github.com/GEMINI-Medicine/gemini-ccsr/blob/master/docs/build/html/index.html) (also see `example_ccsr_v2020-3.csv` for an example of a correctly formatted CCSR file). 


## Usage

To map a list of ICD-10 codes, run:

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

[Malecki et al. (2022). Tools for categorization of diagnostic codes in hospital data: Operationalizing CCSR into a patient data repository.](https://medrxiv.org/cgi/content/short/2022.11.29.22282888v1)

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Version
Version v1.0.0-beta - November 2022
