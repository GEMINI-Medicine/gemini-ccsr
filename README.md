[![Python application](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml/badge.svg)](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml)

# GEMINI: CCSR mapping code (beta version)

The code in this repository maps diagnosis codes from International Classification of Diseases 10th Revision (ICD-10) codes to Clinical Classifications Software Refined (CCSR) categories. For more details, please refer to this paper [Malecki et al. (2022)](https://medrxiv.org/cgi/content/short/2022.11.29.22282888v1) and review the [code documentation](https://rawcdn.githack.com/GEMINI-Medicine/gemini-ccsr/f405fcaa00b994798a0b3d4782be309a27e4c510/docs/build/html/index.html).

Note: The current release is a beta version and is subject to change. 

## Installation & set-up

Please download or clone the repository to a local directory (`<path/to/gemini-ccsr>`). Run `pip3 install --user <path/to/gemini-ccsr>` to install.

By default, the code will map ICD-10 diagnosis codes to CCSR version v2020-3. To change the CCSR version, please download the latest CCSR categorization file from the [CCSR website](https://www.hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp). Please make sure that the CCSR file has been formatted to match the description found in the [documentation](https://rawcdn.githack.com/GEMINI-Medicine/gemini-ccsr/f405fcaa00b994798a0b3d4782be309a27e4c510/docs/build/html/index.html) of the `check_ccsr` function in the `gemini-ccsr formatter` module. You can also check the provided `example_ccsr_v2020-3.csv` file for an example of a correctly formatted CCSR file.

## Usage

To map a list of ICD-10 codes, run:

```python
import pandas as pd
from gemini_ccsr.main import map_icd_to_ccsr

# ICD codes that should be mapped
icd = ['A001', 'C767', 'E90', 'F012', 'G3109', 'N26', 'R1958', 'Z507']

# Official CCSR categorization file
ccsr = pd.read_csv(<path/to/ccsr.csv>)

direct, automatic, semiautomatic, failed = map_icd_to_ccsr(icd, ccsr)
```

For a more detailed example, check `run_example.py` to map the list of ICD-10 diagnosis codes in `example_codes_to_map.csv`. 

**Important:** Please carefully read the [documentation](https://rawcdn.githack.com/GEMINI-Medicine/gemini-ccsr/f405fcaa00b994798a0b3d4782be309a27e4c510/docs/build/html/index.html) for the main `map_icd_to_ccsr` function for a description of the 4 different data frames that are returned by the algorithm (`direct`, `automatic`, `semiautomatic`, and `failed`). Codes that are returned in the `semiautomatic`/`failed` data frames will need to be carefully reviewed by a clinical expert, and may need to be corrected or mapped manually. Similarly, although `automatic` mappings have been shown to be highly accurate in a sample of Canadian ICD-10 codes (see [Malecki et al., 2022)](https://medrxiv.org/cgi/content/short/2022.11.29.22282888v1), we recommend careful inspection of **all** mappings by a subject matter expert. 


## Citation

[Malecki et al. (2022). Tools for categorization of diagnostic codes in hospital data: Operationalizing CCSR into a patient data repository.](https://medrxiv.org/cgi/content/short/2022.11.29.22282888v1)

## License
[MIT license](https://github.com/GEMINI-Medicine/gemini-ccsr/blob/master/LICENSE)

## Versions
+ Version v1.0.1-beta - January 2023 (current version)
+ Version v1.0.0-beta - November 2022
