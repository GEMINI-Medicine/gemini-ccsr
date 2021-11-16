import time

import pandas as pd
from tqdm import tqdm


def get_direct_unmapped(icd, ccsr):
    """Finds ICD 10 codes that directly match CCSR categories.

    Parameters
    ----------
    icd : pd.DataFrame
        A DataFrame with only one column:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        =============  =================================================

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
    direct : pd.DataFrame
        The rows of ccsr that correspond to the ICD 10 codes given in
        icd
    unmapped: pd.DataFrame
        The rows of icd whose entries do not appear in ccsr.
    """
    direct_attempt = pd.merge(ccsr, icd, how='right', on='icd')
    direct_attempt = direct_attempt.where(pd.notnull(direct_attempt), None)
    direct = direct_attempt[
        direct_attempt['ccsr_1'].notna()
    ].sort_values('icd').rename(
        columns={'icd': 'Queried ICD'}).reset_index(drop=True)
    unmapped = direct_attempt[direct_attempt['ccsr_1'].isna()][['icd']]
    return direct, unmapped


def get_predicted(unmapped, ccsr, verbose):
    """Tries to predict the CCSR mapping of each ICD 10 code.

    If a code has no close relatives (ancestors,
    descendants, or siblings) with known CCSR mappings, then it is
    returned in the failed DataFrame. If it has
    ancestors, descedants, or siblings with
    known CCSR mappings but each of these groups' members have no CCSR
    category in common, then it is returned (along with information
    about each of its relatives) in the unresolved DataFrame. If it has
    ancestors, descendants, or siblings with known CCSR mappings and one
    of these groups' members have one or more categories in common, then
    that code is mapped to those categories and returned in the resolved
    DataFrame.


    Parameters
    ----------
    unmapped : pd.DataFrame
        A DataFrame with only one columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        =============  =================================================

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

    verbose : bool
        If True, progress bars are printed.

    Returns
    -------
    resolved : pd.DataFrame
        ICD 10 codes given in unmapped whose CCSR categorizations
        could be predicted based on their relatives.
        Has the following columns:

        =====================  =========================================
        Queried ICD            An ICD 10 code given in the unmapped
                               input (as `str`)
        Deciding Relationship  The relationship that the relative icd
                               code(s) have to Queried ICD (as `str`)
        ccsr_def               default CCSR category (as `str`)
        ccsr_def_desc          default CCSR category description
                               (as `str`)
        ccsr_1                 CCSR category 1 (as `str`)
        ccsr_1_desc            CCSR category 1 description (as `str`)
        ccsr_2                 CCSR category 2 (as `str`)
        ccsr_2_desc            CCSR category 2 description (as `str`)
        ccsr_3                 CCSR category 3 (as `str`)
        ccsr_3_desc            CCSR category 3 description (as `str`)
        ccsr_4                 CCSR category 4 (as `str`)
        ccsr_4_desc            CCSR category 4 description (as `str`)
        ccsr_5                 CCSR category 5 (as `str`)
        ccsr_5_desc            CCSR category 5 description (as `str`)
        ccsr_6                 CCSR category 6 (as `str`)
        ccsr_6_desc            CCSR category 6 description (as `str`)
        =====================  =========================================

    unresolved: pd.DataFrame
        The ICD 10 codes given in unmapped whose CCSR categorization
        could not be inferred, but do have close relatives with an
        official CCSR categorization. Has one row for each (unpredicted
        ICD 10 code, close relative) combination. Has the following
        columns:

        =============  =================================================
        Queried ICD    An ICD 10 code given in the unmapped input
                       (as `str`)
        Relationship   The relationship that icd has to Queried ICD
                       (as `str`)
        icd            ICD 10 code (as `str`)
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

    failed : pd.DataFrame
        The rows of unmapped corresponding to ICD 10 codes who have no
        close relatives.
    """
    related = get_related(unmapped, ccsr, verbose)
    ccsr_colnames = ['ccsr_{}'.format(i) for i in range(1, 6)]
    related[['Deciding Relationship', 'pred_1',
             'pred_2', 'pred_3', 'pred_4', 'pred_5', 'pred_6']] = None
    if verbose:
        print('Inferring mappings based on ICD codes\' relatives.')
        time.sleep(1)
        iterator = tqdm(related['Queried ICD'].unique())
    else:
        iterator = related['Queried ICD'].unique()
    for icd in iterator:
        icd_related = related[related['Queried ICD'] == icd]
        for relation in ['Descendant', 'Sibling', 'Ancestor']:
            icd_relation = icd_related[icd_related['Relationship'] == relation]
            if len(icd_relation) == 0:
                continue
            code_counts = icd_relation[
                ccsr_colnames].stack().value_counts()
            agreed_codes = code_counts[
                code_counts == len(icd_relation)].index.to_list()
            if agreed_codes:
                agreed_codes.extend((6 - len(agreed_codes))*[None])
                cols = ['pred_1', 'pred_2', 'pred_3',
                        'pred_4', 'pred_5', 'pred_6']
                related.loc[
                    related['Queried ICD'] == icd, cols] = agreed_codes
                related.loc[
                    related['Queried ICD'] == icd,
                    'Deciding Relationship'] = relation
                break
    closefam_resolved = related[related['pred_1'].notna()][
        ['Queried ICD', 'Deciding Relationship', 'pred_1',
         'pred_2', 'pred_3', 'pred_4', 'pred_5', 'pred_6']
    ].drop_duplicates().sort_values('Queried ICD').reset_index(drop=True)
    extfam_resolved = get_extfam_resolved(
        related.loc[related['pred_1'].isna(), ['Queried ICD']], ccsr)
    resolved = closefam_resolved.append(
        extfam_resolved).reset_index(drop=True)
    resolved.columns = ['Queried ICD', 'Deciding Relationship', 'ccsr_1',
                        'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6']
    unresolved = related[
        ~related['Queried ICD'].isin(resolved['Queried ICD'])][
        ['Queried ICD', 'Relationship', 'icd', 'ccsr_1',
         'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6']
    ]
    failed = unresolved[unresolved['icd'].isna()][
        ['Queried ICD']
    ].drop_duplicates().sort_values('Queried ICD').reset_index(drop=True)
    unresolved = unresolved[
        unresolved['icd'].notna()
    ].sort_values('Queried ICD').reset_index(drop=True)
    return resolved, unresolved, failed


def get_extfam_resolved(icd_df, ccsr):
    """Uses the output of get_fam_agree to map ICD 10 codes to CCSR.

    Parameters
    ----------
    icd_df : pd.DataFrame
        DataFrame containing ICD 10 codes that should be mapped.

        =============  =================================================
        Queried ICD    ICD 10 code (as `str`)
        =============  =================================================

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
    extfam_resolved: pd.DataFrame
        The ICD 10 codes given in unmapped whose CCSR categorization
        could not be inferred, but do have close relatives with an
        official CCSR categorization. Has one row for each (unpredicted
        ICD 10 code, close relative) combination. Has the following
        columns:

        =============  =================================================
        Queried ICD    An ICD 10 code given in the unmapped input
                       (as `str`)
        Deciding Relationship   'Extended Family'
        pred_1         CCSR category 1 (as `str`)
        pred_2         CCSR category 2 (as `str`)
        pred_3         CCSR category 3 (as `str`)
        pred_4         CCSR category 4 (as `str`)
        pred_5         CCSR category 5 (as `str`)
        pred_6         CCSR category 6 (as `str`)
    """
    icd_df['icd_prefix'] = icd_df['Queried ICD'].str[:3]
    fam_agree = get_fam_agree(ccsr)
    extfam_resolved = icd_df.merge(fam_agree, on='icd_prefix', how='inner')
    extfam_resolved['Deciding Relationship'] = 'Extended Family'
    extfam_resolved = extfam_resolved[
        ['Queried ICD', 'Deciding Relationship', 'pred_1',
         'pred_2', 'pred_3', 'pred_4', 'pred_5', 'pred_6']
    ]
    return extfam_resolved


def get_fam_agree(ccsr):
    """Gets CCSR mappings of ICD 10 code 3 character prefixes.

    If all ICD-10 codes begining with "XYZ" have N CCSR categories
    in common, then "XYZ" and the N CCSR categories are given in
    a row of the returned DataFrame.

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
    fam_agree: pd.DataFrame
        Mappings from 3 character ICD 10 code prefixes to CCSR
        categories. Only has rows if all ICD 10 codes beginning with
        the given prefix agree on one or more CCSR category. Has the
        following columns:

        =============  =================================================
        icd_prefix     The first 3 chars of an ICD 10 code (as `str`)
        pred_1         CCSR category 1 (as `str`)
        pred_2         CCSR category 2 (as `str`)
        pred_3         CCSR category 3 (as `str`)
        pred_4         CCSR category 4 (as `str`)
        pred_5         CCSR category 5 (as `str`)
        pred_6         CCSR category 6 (as `str`)
    """
    ccsr = ccsr.copy()
    ccsr['icd_prefix'] = ccsr['icd'].str[:3]
    ccsr_colnames = ['ccsr_{}'.format(i) for i in range(1, 6)]
    pref_counts = ccsr[['icd_prefix']].value_counts(
        ).reset_index().rename(columns={0: 'N_pref'})
    pref_ccsr_combos = pd.melt(
        ccsr, id_vars='icd_prefix', value_vars=ccsr_colnames,
        value_name='ccsr'
    )[['icd_prefix', 'ccsr']].dropna().value_counts(
        ).reset_index().rename(columns={0: 'N_combo'})
    pref_ccsr_combos = pref_ccsr_combos.merge(
        pref_counts, how='left')
    pref_ccsr_combos['pct_combo'] = (pref_ccsr_combos['N_combo']
                                     / pref_ccsr_combos['N_pref'])
    long_fam_agree = pref_ccsr_combos.loc[
        pref_ccsr_combos['pct_combo'] == 1, ['icd_prefix', 'ccsr']]
    fam_agree = long_fam_agree.groupby('icd_prefix')['ccsr'].apply(
        lambda s: pd.DataFrame([sorted(s.to_list())])).reset_index()
    rn_dict = {i: f'pred_{i+1}' for i in range(6)}
    fam_agree = fam_agree.rename(columns=rn_dict).drop(columns=['level_1'])
    max_col = max([int(s.split('_')[1])
                   for s in fam_agree.columns if 'pred_' in s])
    for i in range(max_col + 1, 7):
        fam_agree[f'pred_{i}'.format(i)] = None
    return fam_agree


def get_related(unmapped, ccsr, verbose):
    """Finds the relatives of each ICD 10 code.

    Relatives are defined as descendants, siblings, or ancestors.

    Parameters
    ----------
    unmapped : pd.DataFrame
        A DataFrame with only one columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        =============  =================================================

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

    verbose : bool
        If True, progress bars are printed.

    Returns
    -------
    relatives: pd.DataFrame
        The descendants, siblings, and ancestors of the unmapped
        ICD 10 codes.

        =============  =================================================
        Queried ICD    An ICD 10 code given in the unmapped input
                       (as `str`)
        Relationship   The relationship that icd has to Queried ICD
                       (as `str`)
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    related_df = None
    if verbose:
        print('Finding ICD codes that are related to unmapped ICD codes.')
        time.sleep(1)
        iterator = tqdm(unmapped.iterrows(), total=unmapped.shape[0])
    else:
        iterator = unmapped.iterrows()
    for i, row in iterator:
        for func in [get_descendants, get_sibs, get_ancs]:
            related = func(row, ccsr)
            if related is not None:
                if related_df is None:
                    related_df = related
                else:
                    related_df = related_df.append(related)
    related = pd.merge(
        unmapped.rename(columns={'icd': 'Queried ICD'}), related_df,
        how='left', on='Queried ICD')
    return related


def get_descendants(row, ccsr):
    """Finds the descendants of a given ICD 10 code.

    Parameters
    ----------
    row : Series
        A Series with one ICD 10 code as its only element.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    Returns
    -------
    related: pd.DataFrame
        The descendants of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in row.
        Relationship   "Descendant".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    descs = ccsr[ccsr['icd'].str.startswith(row['icd'])]
    if len(descs) == 0:
        return None
    for gen_num in range(1, 5):
        generation = descs[descs['icd'].str.len() == len(row['icd']) + gen_num]
        if len(generation) > 0:
            related = generation.drop(columns=['ccsr_def'])
            related.insert(loc=0, column='Relationship', value='Descendant')
            related.insert(loc=0, column='Queried ICD', value=row['icd'])
            return related
    return None


def get_sibs(row, ccsr):
    """Finds the siblings of a given ICD 10 code.

    Parameters
    ----------
    row : Series
        A Series with one ICD 10 code as its only element.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    Returns
    -------
    related: pd.DataFrame
        The siblings of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in row.
        Relationship   "Sibling".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    sibs = ccsr[ccsr['icd'].str[:-1] == row['icd'][:-1]]
    if len(sibs) == 0:
        return None
    related = sibs.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='Relationship', value='Sibling')
    related.insert(loc=0, column='Queried ICD', value=row['icd'])
    return related


def get_ancs(row, ccsr):
    """Finds the ancestors of a given ICD 10 code.

    Parameters
    ----------
    row : Series
        A Series with one ICD 10 code as its only element.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    Returns
    -------
    related: pd.DataFrame
        The ancestors of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in row.
        Relationship   "Ancestor".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    for str_len in range(len(row['icd']) - 1, 2, -1):
        generation = ccsr[ccsr['icd'] == row['icd'][:str_len]]
        if len(generation) > 0:
            related = generation.drop(columns=['ccsr_def'])
            related.insert(loc=0, column='Relationship', value='Ancestor')
            related.insert(loc=0, column='Queried ICD', value=row['icd'])
            return related
    return None
