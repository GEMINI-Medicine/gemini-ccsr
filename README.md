[![Python application](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml/badge.svg)](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml)

# gemini-ccsr
Maps from International Classification of Diseases 10th Revision (ICD10) codes to Clinical Classifications Software Refined (CCSR) categories. 

## Installation

Use the package manager [pip](https://pypi.org/) to install.

```bash
pip install gemini-ccsr
```

## Usage

Download the latest CCSR categorization file from the [CCSR website](https://www.hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp). Please ensure that the CCSR file has been formatted to match the description found in the [documentation](https://github.com/GEMINI-Medicine/gemini-ccsr/blob/master/docs/build/html/index.html). Please see the documentation for a description of the four dataframes returned by `map_icd_to_ccsr`.

```python
import pandas as pd

from gemini_ccsr.main import map_icd_to_ccsr

# ICD codes that should be mapped
icd = ['A000', 'A001', 'A0101', 'A085']
# Official CCSR categorization file
ccsr = pd.read_csv(<ccsr_filepath>)

direct, resolved, unresolved, failed = map_icd_to_ccsr(icd, ccsr)
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
