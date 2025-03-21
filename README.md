[![Python application](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml/badge.svg)](https://github.com/GEMINI-Medicine/gemini-ccsr/actions/workflows/python-app.yml)

# GEMINI: CCSR mapping code

The code in this repository maps diagnosis codes from the International Classification of Diseases 10th Revision, Canadian version (ICD-10-CA) to broader, more clinically meaningful categories defined by the Clinical Classifications Software Refined (CCSR). For more details, please refer to this paper [Malecki et al. (2024)](https://www.sciencedirect.com/science/article/pii/S1386505624001710) and review the [code documentation](https://rawcdn.githack.com/GEMINI-Medicine/gemini-ccsr/da295728ade888f96b5a1f9f3b5ed99464651f08/docs/build/index.html).

## Installation

Please download (and unzip) or clone the repository to a local directory (`"path/to/gemini-ccsr"`). Then simply run `pip install --user "path/to/gemini-ccsr/"`.

If you encounter an SSL certificate verification error during installation, try running the following: `pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --user "path/to/gemini-ccsr/"`.

Please make sure all dependencies are installed successfully. You can try running `pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r "path/to/gemini-ccsr/requirements.txt"` to install all dependencies.

Finally, to import from this package, you may need to add the install location (found via `pip show gemini-ccsr`) to your $PYTHONPATH so Python knows where to look for it:

```
import sys
sys.path.append("path/from/pip_show_gemini-ccsr/")

from gemini_ccsr.main import map_icd_to_ccsr
```

If you have trouble installing the package, you can also use `sys.path.append("path/to/gemini-ccsr")` to direct Python to the path where you saved the repository (instead of the install location).
In this case, the dependencies `numpy`, `pandas`, `tqdm`, and `time` will still need to be installed.


## Official CCSR tool

By default, the code will map ICD-10 diagnosis codes based on the official CCSR version v2020-3. To change the CCSR version, please download the latest CCSR categorization file from the [CCSR website](https://www.hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp). Please make sure that the CCSR file has been formatted to match the description found in the [documentation](https://rawcdn.githack.com/GEMINI-Medicine/gemini-ccsr/da295728ade888f96b5a1f9f3b5ed99464651f08/docs/build/index.html) of the `check_ccsr` function in the `gemini-ccsr formatter` module. You can also check the provided `example_ccsr_v2020-3.csv` file for an example of a correctly formatted CCSR file.

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

**Important:** Please carefully read the [documentation](https://rawcdn.githack.com/GEMINI-Medicine/gemini-ccsr/da295728ade888f96b5a1f9f3b5ed99464651f08/docs/build/index.html) for the main `map_icd_to_ccsr` function for a description of the 4 different data frames that are returned by the algorithm (`direct`, `automatic`, `semiautomatic`, and `failed`). Codes that are returned in the `semiautomatic`/`failed` data frames will need to be carefully reviewed by a clinical expert, and may need to be corrected or mapped manually. Similarly, although `automatic` mappings have been shown to be highly accurate in a sample of Canadian ICD-10 codes (see [Malecki et al., 2024)](https://www.sciencedirect.com/science/article/pii/S1386505624001710), we recommend careful inspection of **all** mappings by a subject matter expert. 


## Citation

[Malecki et al. (2024). Development and external validation of tools for categorizing diagnosis codes in international hospital data.](https://www.sciencedirect.com/science/article/pii/S1386505624001710)

## License
[MIT license](https://github.com/GEMINI-Medicine/gemini-ccsr/blob/main/LICENSE)

