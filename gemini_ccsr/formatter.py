import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None


def get_default_map(official_ccsr):
    """Returns a mapping from CCSR categories to their default.

    Parameters
    ----------
    official_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_def       default CCSR category (as `str`)
        ccsr_def_desc  default CCSR category description (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_1_desc    CCSR category 1 description (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_2_desc    CCSR category 2 description (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_3_desc    CCSR category 3 description (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_4_desc    CCSR category 4 description (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_5_desc    CCSR category 5 description (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        ccsr_6_desc    CCSR category 6 description (as `str`)
        =============  =================================================

    Returns
    -------
    default_map : dict of tuple : str
        a dictionary mapping from a group of CCSR categories
        (alphabetically sorted) to their default category.
    """
    official_ccsr = official_ccsr.copy()
    ccsr_cols = ['ccsr_{}'.format(i) for i in range(1, 7)]
    official_ccsr = official_ccsr[['ccsr_def'] + ccsr_cols].drop_duplicates()
    ccsr_defaults = official_ccsr[['ccsr_def']].copy()
    ccsr_defaults['ccsr_tup'] = official_ccsr[ccsr_cols].apply(
        lambda row: tuple(sorted(row[row.notna()].to_list())), axis=1)
    default_map = ccsr_defaults.set_index('ccsr_tup').to_dict()['ccsr_def']
    return default_map


def get_desc_df(official_ccsr):
    """Returns a dataframe map from a CCSR category to its description.

    Parameters
    ----------
    official_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_def       default CCSR category (as `str`)
        ccsr_def_desc  default CCSR category description (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_1_desc    CCSR category 1 description (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_2_desc    CCSR category 2 description (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_3_desc    CCSR category 3 description (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_4_desc    CCSR category 4 description (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_5_desc    CCSR category 5 description (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        ccsr_6_desc    CCSR category 6 description (as `str`)
        =============  =================================================

    Returns
    -------
    ccsr_desc : pd.DataFrame
        DataFrame mapping from CCSR categories to their descriptions.
        Has the following columns:

        =========  =====================================================
        ccsr       CCSR category (as `str)
        ccsr_desc  CCSR category desciption (as `str`)
        =========  =====================================================
    """
    new_cols = ['ccsr', 'ccsr_desc']
    def_old_cols = ['ccsr_def', 'ccsr_def_desc']
    ccsr_desc = pd.concat(
        [official_ccsr[def_old_cols].set_axis(new_cols, axis=1)] +
        [official_ccsr[
            ['ccsr_{}'.format(i), 'ccsr_{}_desc'.format(i)]
            ].set_axis(new_cols, axis=1) for i in range(1, 7)]
    ).drop_duplicates(ignore_index=True)
    ccsr_desc = ccsr_desc.dropna(how='all')
    ccsr_desc = ccsr_desc.sort_values('ccsr').reset_index(drop=True)
    return ccsr_desc


def add_descs(edit_ccsr, official_ccsr):
    """Adds CCSR descriptions to a DataFrame with CCSR columns.

    Parameters
    ----------
    edit_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        ccsr_def       (Optional) the default CCSR category (as `str`)
        =============  =================================================

    official_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_def       default CCSR category (as `str`)
        ccsr_def_desc  default CCSR category description (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_1_desc    CCSR category 1 description (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_2_desc    CCSR category 2 description (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_3_desc    CCSR category 3 description (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_4_desc    CCSR category 4 description (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_5_desc    CCSR category 5 description (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        ccsr_6_desc    CCSR category 6 description (as `str`)
        =============  =================================================

    Returns
    -------
    edit_ccsr : pd.DataFrame
        The edit_ccsr input dataframe with description columns added.
    """
    ccsr_desc_df = get_desc_df(official_ccsr)
    ccsr_desc_map = ccsr_desc_df.set_index('ccsr').to_dict()['ccsr_desc']
    ccsr_colnames = ['ccsr_{}'.format(i) for i in range(1, 7)]
    if not set(ccsr_colnames).issubset(edit_ccsr.columns):
        raise ValueError('No recognized ccsr columns.')
    if 'ccsr_def' in edit_ccsr.columns:
        ccsr_colnames.insert(0, 'ccsr_def')
    all_ccsr_colnames = []
    for colname in ccsr_colnames:
        desc_name = colname + '_desc'
        edit_ccsr[desc_name] = edit_ccsr[colname].map(
            ccsr_desc_map, na_action='ignore').replace({np.nan: None})
        all_ccsr_colnames.extend([colname, desc_name])
    col_order = ([col for col in edit_ccsr.columns
                  if col not in all_ccsr_colnames]
                 + all_ccsr_colnames)
    edit_ccsr = edit_ccsr[col_order]
    return edit_ccsr


def add_default(edit_ccsr, official_ccsr):
    """Adds default CCSR categories to a DataFrame with CCSR categories.

    Parameters
    ----------
    edit_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    official_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_def       default CCSR category (as `str`)
        ccsr_def_desc  default CCSR category description (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_1_desc    CCSR category 1 description (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_2_desc    CCSR category 2 description (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_3_desc    CCSR category 3 description (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_4_desc    CCSR category 4 description (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_5_desc    CCSR category 5 description (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        ccsr_6_desc    CCSR category 6 description (as `str`)
        =============  =================================================

    Returns
    -------
    ccsr : pd.DataFrame
        The edit_ccsr input DataFrame with a CCSR default category
        column added.
    """
    edit_ccsr = edit_ccsr.copy()
    default_map = get_default_map(official_ccsr)
    ccsr_cols = ['ccsr_{}'.format(i) for i in range(1, 7)]
    edit_ccsr['ccsr_tup'] = edit_ccsr[ccsr_cols].apply(
        lambda row: tuple(sorted(row[row.notna()].to_list())), axis=1)
    edit_ccsr['ccsr_def'] = edit_ccsr['ccsr_tup'].apply(
        lambda tup: default_map.get(tup, 'XXX000'))
    edit_ccsr = edit_ccsr.drop(columns=['ccsr_tup'])
    return edit_ccsr


def check_icd(query_icd):
    """Checks that query_icd is formatted correctly.

    Parameters
    ----------
    query_icd : array_like
        A one-dimensional array_like object containing the ICD10 codes
        that should be mapped.

    Returns
    -------
    query_icd : pd.DataFrame
        A DataFrame whose only column is the input query_icd list
        (as `str`)
    """
    try:
        temp = np.array(query_icd)
    except (ValueError, TypeError):
        raise TypeError('query_icd must be array-like.')
    if temp.ndim != 1:
        raise ValueError('query_icd must be one-dimensional.')
    query_icd = list(set(query_icd))
    # remove NaNs
    query_icd = [e for e in query_icd if e == e]
    query_icd = sorted(query_icd)
    query_icd = np.array(query_icd, dtype=str)
    query_icd = pd.DataFrame(query_icd, columns=['icd'])
    return query_icd


def check_ccsr(ccsr):
    """Checks that the ccsr DataFrame is formatted correctly.

    Parameters
    ----------
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_def       default CCSR category (as `str`)
        ccsr_def_desc  default CCSR category description (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_1_desc    CCSR category 1 description (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_2_desc    CCSR category 2 description (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_3_desc    CCSR category 3 description (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_4_desc    CCSR category 4 description (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_5_desc    CCSR category 5 description (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        ccsr_6_desc    CCSR category 6 description (as `str`)
        =============  =================================================

    Returns
    -------
    ccsr : pd.DataFrame
        The input DataFrame with `only` the mandatory columns.
    """
    ccsr[(ccsr == 'NA') | (ccsr == '')] = None
    ccsr = ccsr.where(pd.notnull(ccsr), None)
    cols = ['icd', 'ccsr_def', 'ccsr_def_desc',
            'ccsr_1', 'ccsr_1_desc', 'ccsr_2', 'ccsr_2_desc',
            'ccsr_3', 'ccsr_3_desc', 'ccsr_4', 'ccsr_4_desc',
            'ccsr_5', 'ccsr_5_desc', 'ccsr_6', 'ccsr_6_desc']
    missing_cols = [colname for colname in cols
                    if colname not in ccsr.columns]
    if missing_cols:
        raise ValueError(
            'ccsr DataFrame is missing columns: '
            '{}'.format(', '.join(missing_cols)))
    ccsr = ccsr[cols]
    return ccsr
