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
        icd            ICD-10 code (as `str`)
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
        lambda row: tuple(sorted(row[(row.notna()) & (row != ' ')].to_list())), axis=1)
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
        icd            ICD 10 codes (as `str`)
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

        =============  =====================================================
        ccsr           CCSR category (as `str)
        ccsr_desc      CCSR category desciption (as `str`)
        =============  =====================================================
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


def add_default(output_ccsr, official_ccsr):
    """Adds default CCSR categories to a DataFrame with automatically
    mapped CCSR categories. Note: Semi-automatically/failed diagnosis codes
    are returned without default CCSR category as those DataFrames require
    additional validation and/or manual mapping. The default CCSR category for
    those codes should be added after validation has been completed.

    Parameters
    ----------
    output_ccsr : pd.DataFrame
        DataFrame containing the output of the automatically mapped ICD-10
        codes. Must have the following columns:

        ======================  ===============================================
        queried_icd             ICD-10 codes that were mapped automatically
                                (as `str`)
        deciding_relationship   The relationship that the related ICD-10 codes
                                in official_ccsr have to the queried_icd
                                (as `str`)
        related_codes           A list of all ICD-10 codes that were found in
                                official_ccsr and have the
                                `deciding_relationship` to queried_icd (as
                                `list`)
        ccsr_1                  CCSR category 1 (as `str`)
        ccsr_2                  CCSR category 2 (as `str`)
        ccsr_3                  CCSR category 3 (as `str`)
        ccsr_4                  CCSR category 4 (as `str`)
        ccsr_5                  CCSR category 5 (as `str`)
        ccsr_6                  CCSR category 6 (as `str`)
        ======================  ===============================================

    official_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        ==============  =================================================
        icd             ICD 10 codes (as `str`)
        ccsr_def        default CCSR category (as `str`)
        ccsr_def_desc   default CCSR category description (as `str`)
        ccsr_1          CCSR category 1 (as `str`)
        ccsr_1_desc     CCSR category 1 description (as `str`)
        ccsr_2          CCSR category 2 (as `str`)
        ccsr_2_desc     CCSR category 2 description (as `str`)
        ccsr_3          CCSR category 3 (as `str`)
        ccsr_3_desc     CCSR category 3 description (as `str`)
        ccsr_4          CCSR category 4 (as `str`)
        ccsr_4_desc     CCSR category 4 description (as `str`)
        ccsr_5          CCSR category 5 (as `str`)
        ccsr_5_desc     CCSR category 5 description (as `str`)
        ccsr_6          CCSR category 6 (as `str`)
        ccsr_6_desc     CCSR category 6 description (as `str`)
        ==============  =================================================

    Returns
    -------
    ccsr : pd.DataFrame
        The `output_ccsr` input DataFrame with a CCSR default category
        column added.
    """

    output_ccsr = output_ccsr.copy()
    default_map = get_default_map(official_ccsr)
    ccsr_cols = ['ccsr_{}'.format(i) for i in range(1, 7)]
    # add all mapped CCSR1-6 codes as tuple in last column
    output_ccsr['ccsr_tup'] = output_ccsr[ccsr_cols].apply(
        lambda row: tuple(sorted(row[row.notna()].to_list())), axis=1)

    # replace with None if specified key does not exist in default map
    output_ccsr['ccsr_def'] = output_ccsr['ccsr_tup'].apply(
        lambda tup: default_map.get(tup, None))

    iterator = output_ccsr.loc[output_ccsr['ccsr_def'].isna(), 'queried_icd']

    for icd in iterator:

        # if only 1 shared category (CCSR1, but not CCSR2) -> use that one as default
        if pd.isnull(output_ccsr.loc[output_ccsr['queried_icd'] == icd, 'ccsr_2']).bool():
            output_ccsr.loc[output_ccsr['queried_icd'] == icd, 'ccsr_def'] = output_ccsr.loc[
                output_ccsr['queried_icd'] == icd, 'ccsr_1']

        # if more than one shared category, which one of shared categories is most commonly default among related codes?
        else:
            rel_tup = output_ccsr.loc[output_ccsr['queried_icd'] == icd]['related_codes'].values[0]
            rel = official_ccsr.loc[official_ccsr['icd'].isin(rel_tup)]

            # get categories that are shared between all related codes
            shared_cat = output_ccsr.loc[output_ccsr['queried_icd'] == icd, 'ccsr_tup'].values[0]
            # are any of the shared categories default categories? If yes, which one most frequent one?
            shared_def = rel.loc[rel['ccsr_def'].isin(shared_cat), 'ccsr_def']
            if not shared_def.empty:
                output_ccsr.loc[
                    output_ccsr['queried_icd'] == icd, 'ccsr_def'] = shared_def.value_counts().sort_values(
                        ascending=False).index[0]

    output_ccsr = output_ccsr.drop(columns=['ccsr_tup'])

    return output_ccsr


def add_descs(output_ccsr, official_ccsr, automatic_format=True):

    """Adds CCSR descriptions to the output DataFrame with mapped CCSR
    categories. This is only relevant for the automatic and semi-automatic
    DataFrames. Since the automatic vs. semi-automatic output DataFrames are
    formatted slightly differently, the `automatic_format` flag indicates which
    format should be assumed.

    Parameters
    ----------
    output_ccsr : pd.DataFrame
        DataFrame containing the output of the semi-/automatically mapped
        ICD-10 codes. The structure and content of this DataFrama depends on
        whether `output_ccsr` corresponds to automatically or semi-automatically
        mapped codes.
        For automatic codes, `output_ccsr` contains any automatically mapped
        ICD-10 codes, including their mapped CCSR 1-6 categories in separate
        columns as well as an additional column coding the CCSR default
        category:

        ======================  ===============================================
        queried_icd             ICD-10 codes that were mapped automatically
                                (as `str`)
        deciding_relationship   The relationship that the related ICD-10 codes
                                in official_ccsr have to the queried_icd
                                (as `str`)
        related_codes           A list of all ICD-10 codes that were found in
                                official_ccsr and have the
                                `deciding_relationship` to queried_icd
                                (as `list`)
        ccsr_1                  CCSR category 1 (as `str`)
        ccsr_2                  CCSR category 2 (as `str`)
        ccsr_3                  CCSR category 3 (as `str`)
        ccsr_4                  CCSR category 4 (as `str`)
        ccsr_5                  CCSR category 5 (as `str`)
        ccsr_6                  CCSR category 6 (as `str`)
        ccsr_def                For automatic codes only: CCSR default category
                                assigned by the add_default function (as `str`)
        ======================  ===============================================

        For semi-automatic codes, `output_ccsr` contains any semi-automatically
        mapped ICD-10 codes, where each row of ccsr_1 corresponds to a
        candidate CCSR category. In this case, no CCSR default category exists.
        Must have the following columns:

        ==================  ================================================
        queried_icd         ICD-10 codes that were mapped semi-automatically
                            (as `str`)
        relationship        The type of relationship (`Close`/`Distant`)
                            that the related ICD-10 codes in official_ccsr
                            have to the queried_icd (as `str`)
        ccsr_1              Predicted CCSR categories in separate rows
                            (as `str`)
        prct_fam_agree      Percentage of related diagnosis codes in the
                            official CCSR file that share the predicted CCSR
                            category (as `num`)
        ==================  ================================================

    official_ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        ==============  =================================================
        icd             ICD 10 codes (as `str`)
        ccsr_def        default CCSR category (as `str`)
        ccsr_def_desc   default CCSR category description (as `str`)
        ccsr_1          CCSR category 1 (as `str`)
        ccsr_1_desc     CCSR category 1 description (as `str`)
        ccsr_2          CCSR category 2 (as `str`)
        ccsr_2_desc     CCSR category 2 description (as `str`)
        ccsr_3          CCSR category 3 (as `str`)
        ccsr_3_desc     CCSR category 3 description (as `str`)
        ccsr_4          CCSR category 4 (as `str`)
        ccsr_4_desc     CCSR category 4 description (as `str`)
        ccsr_5          CCSR category 5 (as `str`)
        ccsr_5_desc     CCSR category 5 description (as `str`)
        ccsr_6          CCSR category 6 (as `str`)
        ccsr_6_desc     CCSR category 6 description (as `str`)
        ==============  =================================================

    automatic_format : bool
        Flag indicating whether `output_ccsr` DataFrame corresponds to
        automatically mapped codes (True) or semi-automatically mapped codes
        (False).

    Returns
    -------
    output_ccsr : pd.DataFrame
        The `output_ccsr` input dataframe with description columns added. Format
        will slightly differ between automatic vs. semi-automatic output
        DataFrames.
    """
    ccsr_desc_df = get_desc_df(official_ccsr)
    ccsr_desc_map = ccsr_desc_df.set_index('ccsr').to_dict()['ccsr_desc']
    if automatic_format:
        ccsr_colnames = ['ccsr_{}'.format(i) for i in range(1, 7)]
    else:
        ccsr_colnames = ['ccsr_1']

    if not set(ccsr_colnames).issubset(output_ccsr.columns):
        raise ValueError('No recognized ccsr columns.')
    if 'ccsr_def' in output_ccsr.columns:
        ccsr_colnames.insert(0, 'ccsr_def')
    all_ccsr_colnames = []
    for colname in ccsr_colnames:
        desc_name = colname + '_desc'
        output_ccsr[desc_name] = output_ccsr[colname].map(
            ccsr_desc_map, na_action='ignore').replace({np.nan: None})
        all_ccsr_colnames.extend([colname, desc_name])
    col_order = ([col for col in output_ccsr.columns
                  if col not in all_ccsr_colnames]
                 + all_ccsr_colnames)
    output_ccsr = output_ccsr[col_order]

    if automatic_format is False:  # For semi-automatic codes, rename from ccsr_1 to pred_ccsr and change column order
        output_ccsr.rename(columns={'ccsr_1': 'pred_ccsr', 'ccsr_1_desc': 'pred_ccsr_desc'}, inplace=True)
        output_ccsr = output_ccsr[['queried_icd', 'pred_ccsr', 'pred_ccsr_desc', 'relationship', 'prct_fam_agree']]

    return output_ccsr


def check_icd(query_icd):

    """Checks that query_icd is formatted correctly.

    Parameters
    ----------
    query_icd : array_like
        A one-dimensional array_like object containing the ICD-10 codes
        that should be mapped.

        ===============  =====================================================
        query_icd        ICD-10 codes to be mapped (as `str`)
        ===============  =====================================================

    Returns
    -------
    query_icd : pd.DataFrame
        A DataFrame whose only column is the input query_icd list
        (as `str`)

        ===============  =====================================================
        query_icd        Correctly formatted ICD-10 codes to be mapped
                         (as `str`)
        ===============  =====================================================

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

    # Make sure all codes start with capitalized letters
    query_icd = [i.capitalize() for i in query_icd]

    query_icd = sorted(query_icd)
    query_icd = np.array(query_icd, dtype=str)
    query_icd = pd.DataFrame(query_icd, columns=['icd'])

    return query_icd


def check_ccsr(ccsr):

    """Checks that the ccsr DataFrame containing the official CCSR mapping
    is formatted correctly.

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

    ccsr.replace(['', ' ', '\x00', 'NA', None], None, inplace=True)
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
