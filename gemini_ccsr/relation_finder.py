import time

import pandas as pd
from tqdm import tqdm


def get_direct_unmapped(icd, ccsr):

    """Finds ICD-10 codes that match a diagnosis code in the official CCSR file
    and can be mapped directly to the corresponding CCSR categories.

    Parameters
    ----------
    icd : pd.DataFrame
        A DataFrame with only one column:

        =============  =================================================
        icd            ICD-10 codes (as `str`)
        =============  =================================================

    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================================
        icd            ICD-10 codes (as `str`)
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
        The rows of `ccsr` for ICD-10 codes in `icd` that matched diagnosis
        codes in the official CCSR mapping file.

        =============  =================================================
        icd            ICD-10 codes (as `str`)
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

    unmapped: pd.DataFrame
        The rows of `icd` whose entries do not appear in `ccsr`.

        =============  =================================================
        icd            ICD-10 codes that could not be mapped directly
                       (as `str`)
        =============  =================================================

    """
    print('1) Getting direct mapping for existing codes in official CCSR.')
    direct_attempt = pd.merge(ccsr, icd, how='right', on='icd')
    direct_attempt = direct_attempt.where(pd.notnull(direct_attempt), None)
    direct = direct_attempt[
        direct_attempt['ccsr_1'].notna()
    ].sort_values('icd').rename(
        columns={'icd': 'queried_icd'}).reset_index(drop=True)
    unmapped = direct_attempt[direct_attempt['ccsr_1'].isna()][['icd']]
    return direct, unmapped


def get_predicted(unmapped, ccsr, verbose):
    """Tries to predict the CCSR mapping of each ICD-10 code that could not
    be mapped directly.

    For any unmapped codes, the algorithm first checks for closely related
    codes (`Children`, `Siblings`, or `Parents`) with known CCSR mappings.
    If no close relatives are found, the algorithm checks for distantly related
    codes (`Half-siblings`, `Cousins`, or `Extended family`).

    If no close/distant relatives are found, the diagnosis code is returned in
    the `failed` DataFrame and needs to be mapped manually.

    If a diagnosis code has close/distant relatives with known CCSR
    mappings but none of the CCSR categories are shared by *all* identified
    family members, then the code is returned in the `semiautomatic` DataFrame
    (along with information about what percentage of family members share each
    candidate CCSR category).

    If a diagnosis code has close/distant relatives all family members have
    one or more categories in common, then that code is mapped to all shared
    categories and returned in the `automatic` DataFrame.



    Parameters
    ----------
    unmapped : pd.DataFrame
        A DataFrame with only one column containing any ICD-10 codes that could
        not be mapped directly:

        ==============  =================================================
        icd             ICD-10 codes (as `str`)
        ==============  =================================================

    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        ==============  =================================================
        icd             ICD-10 codes (as `str`)
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

    verbose : bool
        If True, progress bars are printed.

    Returns
    -------
    automatic : pd.DataFrame
        Predicted CCSR categories for ICD-10 codes that could not be mapped directly,
        but whose CCSR categorization could be inferred based on related codes.
        Has the following columns:

        ======================  ===============================================
        queried_icd             ICD-10 codes that were mapped automatically
                                (as `str`)
        deciding_relationship   The relationship that the related ICD-10 codes
                                in `official_ccsr` have to the `queried_icd`
                                (as `str`)
        related_codes           A list of all ICD-10 codes that were found in
                                `official_ccsr` and have the
                                `deciding_relationship` to `queried_icd`
                                (as `list`)
        ccsr_def                default CCSR category (as `str`)
        ccsr_def_desc           default CCSR category description
                                (as `str`)
        ccsr_1                  CCSR category 1 (as `str`)
        ccsr_1_desc             CCSR category 1 description (as `str`)
        ccsr_2                  CCSR category 2 (as `str`)
        ccsr_2_desc             CCSR category 2 description (as `str`)
        ccsr_3                  CCSR category 3 (as `str`)
        ccsr_3_desc             CCSR category 3 description (as `str`)
        ccsr_4                  CCSR category 4 (as `str`)
        ccsr_4_desc             CCSR category 4 description (as `str`)
        ccsr_5                  CCSR category 5 (as `str`)
        ccsr_5_desc             CCSR category 5 description (as `str`)
        ccsr_6                  CCSR category 6 (as `str`)
        ccsr_6_desc             CCSR category 6 description (as `str`)
        ======================  ===============================================

    semiautomatic: pd.DataFrame
        Predicted CCSR categories for ICD-10 codes that could not be mapped
        directly or automatically. These are diagnosis codes for which the
        algorithm identified related codes, but none of the CCSR categories
        are shared by all related codes (i.e., CCSR mapping could not be
        inferred automatically). Has one row for each [ICD-10 code, candidate
        CCSR] combination. Additionally provides the percentage of related
        codes that share each predicted CCSR category. Users need to review
        the output file to exclude any rows with incorrect predictions.
        Has the following columns:

        ===============  ======================================================
        queried_icd      ICD-10 codes that were mapped semi-automatically.
                         (as `str`)
        relationship     The relationship that the queried ICD-10 code
                         has to related codes in `official_ccsr`. Either "Close"
                         or "Distant" (as `str`)
        pred_ccsr        Predicted CCSR category (as `str`)
        pred_ccsr_desc   Predicted CCSR category description (as `str`)
        prct_fam_agree   Percentage of related diagnosis codes in the official
                         CCSR file that share the predicted CCSR category
                         (as `num`)
        ===============  ======================================================

    failed : pd.DataFrame
        The rows of `query_icd` corresponding to ICD-10 codes that do not have
        any closely or distantly related codes in the official CCSR file.
    """

    # %% PREDICTIONS BASED ON CLOSELY RELATED CODES
    ccsr_colnames = ['ccsr_{}'.format(i) for i in range(1, 7)]

    # Get codes that are unmapped after direct mapping
    related_close = unmapped.sort_values('icd')
    related_close[[
        'deciding_relationship', 'ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6', 'related_codes']] = None

    closefam_resolved = pd.DataFrame(columns=['ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6',
                                              'deciding_relationship', 'queried_icd', 'related_codes'])
    closefam_unresolved = pd.DataFrame([])
    closefam_failed = pd.DataFrame(columns=['queried_icd'])

    if verbose:
        print('2) Inferring mappings based on ICD codes\' close relatives.')
        time.sleep(1)
        iterator = tqdm(related_close['icd'])
    else:
        iterator = related_close['icd']

    # loop through each unmapped ICD code and check agreement among closely related codes' CCSR categories
    # starting with children, then siblings, then parents
    for icd in iterator:

        icd_related = get_closely_related(icd, ccsr, verbose)
        automatic = False

        icd_relation_temp = pd.DataFrame([])  # keep track of all categories that occured among any close relatives

        if not icd_related.empty:  # if any close relationships found
            for relation in ['Children', 'Siblings', 'Parents']:
                icd_relation = icd_related[icd_related['relationship'] == relation]
                if len(icd_relation) == 0:  # check if close family member exists, if not, check next close family group
                    continue

                # keep track of all categories that occured among any close relatives
                icd_relation_temp = pd.concat([icd_relation_temp, icd_relation])

                code_counts = icd_relation[
                    ccsr_colnames].stack().value_counts()

                # identify CCSR1-6 categories that match across all children/sibl/parent codes
                agreed_codes = code_counts[
                    code_counts == len(icd_relation)].index.to_list()

                if agreed_codes:
                    agreed_codes.extend((6 - len(agreed_codes))*[None])

                    # Create new dataframe with automatic code
                    res = pd.DataFrame({'queried_icd': icd,
                                        'deciding_relationship': relation,
                                        'related_codes': [list(
                                           icd_related.loc[icd_related['relationship'] == relation, 'icd'].values)]})

                    res.loc[0, ['ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6']] = agreed_codes

                    closefam_resolved = pd.concat([closefam_resolved, res])

                    automatic = True
                    break

            # if no category agreement found, get all unique categories and percentage of overlap across all relationship
            if not automatic and not icd_relation_temp.empty:
                # for each category among any close family members, get percentage of shared
                code_perc = pd.Series(
                    100*icd_relation_temp[ccsr_colnames].stack().value_counts() /
                    len(icd_relation_temp)).to_frame(name='prct_fam_agree').round(decimals=2)
                code_perc['queried_icd'] = icd
                code_perc.sort_values(by=['prct_fam_agree'], ascending=False)

                if len(code_perc) == 0:  # if no categories that are shared by at least 5% of related codes, return as failed
                    closefam_failed = pd.concat([closefam_failed, pd.DataFrame({'queried_icd': [icd]})])
                else:  # add any shared categories among related codes
                    code_perc['relationship'] = 'Close'
                    closefam_unresolved = pd.concat([closefam_unresolved, code_perc])

        else:  # if no close relationships found at all
            closefam_failed = pd.concat([closefam_failed,pd.DataFrame({'queried_icd': [icd]})])

    if not closefam_unresolved.empty:
        closefam_unresolved = closefam_unresolved.reset_index(drop=False).rename(
            columns={'index': 'ccsr_1'}).loc[:,['queried_icd', 'ccsr_1', 'prct_fam_agree', 'relationship']]

    # %% PREDICTIONS BASED ON DISTANTLY RELATED CODES

    distfam_resolved = pd.DataFrame(columns=[
        'ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6', 'deciding_relationship', 'queried_icd', 'related_codes'])
    distfam_unresolved = pd.DataFrame([])
    distfam_failed = pd.DataFrame(columns=['queried_icd'])

    if not closefam_failed.empty:

        # Get codes that are still failed based on close family relationships and check for distant relationships
        related_dist = closefam_failed.sort_values('queried_icd').rename(columns={'queried_icd': 'icd'})
        related_dist[[
            'deciding_relationship', 'ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6', 'related_codes']] = None

        if verbose:
            print('3) Inferring mappings based on ICD codes\' distant relatives.')
            time.sleep(1)
            iterator = tqdm(related_dist['icd'])
        else:
            iterator = related_dist['icd']

        # loop through each unmapped ICD code and check agreement among distantly related codes' CCSR categories
        # starting with half-siblings, then cousins, then extended family
        # break as soon as any relationship type was found (only closest type of distant relationships contributes to mapping)
        for icd in iterator:

            icd_related = get_distantly_related(icd, ccsr, verbose)  # get related codes of queried_icd code
            automatic = False

            icd_relation_temp = pd.DataFrame([])  # keep track of all categories that occured among any close relatives

            if not icd_related.empty:  # if any distant relationships found
                for relation in ['Half-Siblings', 'Cousins', 'Extended Family']:
                    icd_relation = icd_related[icd_related['relationship'] == relation]
                    if len(icd_relation) == 0:  # check if distant family member exists, if not, check next distant family group
                        continue

                    if icd_relation_temp.empty:
                        # DIFFERENCE TO CLOSE relationships: Only include categories from 'closest' distant family group
                        # (e.g., if half-siblings exist, only include those and ignore cousins/extended family)
                        # keep track of all categories that occured among any distant relatives
                        icd_relation_temp = pd.concat([icd_relation_temp, icd_relation])

                    code_counts = icd_relation[
                        ccsr_colnames].stack().value_counts()

                    # identify CCSR1-6 categories that match across all half-siblings/cousins/ext. fam. codes
                    agreed_codes = code_counts[
                        code_counts == len(icd_relation)].index.to_list()

                    if agreed_codes:
                        agreed_codes.extend((6 - len(agreed_codes))*[None])

                        # Create new dataframe with automatic code
                        res = pd.DataFrame({'queried_icd': icd,
                                            'deciding_relationship': relation,
                                            'related_codes': [list(icd_related.loc[
                                                icd_related['relationship'] == relation,'icd'].values)]})

                        res.loc[0, ['ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6']] = agreed_codes

                        distfam_resolved = pd.concat([distfam_resolved, res])
                        automatic = True

                    if len(icd_relation) > 0:
                        # for distantly related codes only: break loop right after 1st type of relationship was identified
                        break

                # if no category agreement found, get all unique categories and percentage of overlap across all relationships
                if not automatic and not icd_relation_temp.empty:
                    # for each category among any distant family members, get percentage of shared
                    code_perc = pd.Series(
                        100*icd_relation_temp[ccsr_colnames].stack().value_counts() /
                        len(icd_relation_temp)).to_frame(name='prct_fam_agree').round(decimals=2) 
                    code_perc['queried_icd'] = icd

                    if len(code_perc) == 0:  # if no categories that are shared by at least 5% of related codes, return as failed
                        distfam_failed = pd.concat([distfam_failed,pd.DataFrame({'queried_icd': [icd]})])
                    else:  # add any found categories shared among related codes
                        code_perc['relationship'] = 'Distant' 
                        distfam_unresolved = pd.concat([distfam_unresolved, code_perc])

            else:  # if no distant relationships found at all
                distfam_failed = pd.concat([distfam_failed,pd.DataFrame({'queried_icd': [icd]})])

        if not distfam_unresolved.empty:
            distfam_unresolved = distfam_unresolved.reset_index(drop=False).rename(
                columns={'index': 'ccsr_1'}).loc[:,['queried_icd', 'ccsr_1', 'prct_fam_agree', 'relationship']]

    # %% MERGE CLOSELY/DISTANTLY RELATED & RESOLVED CODES, RETURN WITH UNRESOLVED & FAILED CODES
    automatic = pd.concat([closefam_resolved,
        distfam_resolved]).reset_index(drop=True)

    automatic = automatic[['queried_icd', 'deciding_relationship', 'ccsr_1',
                        'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6', 'related_codes']]

    automatic.sort_values(["queried_icd"],axis = 0, ascending = [True],inplace = True,ignore_index=True)

    # semiautomatic
    semiautomatic = pd.DataFrame(columns = ['queried_icd', 'ccsr_1', 'prct_fam_agree', 'relationship'])
    semiautomatic = pd.concat([semiautomatic,closefam_unresolved,
        distfam_unresolved]).reset_index(drop=True)

    semiautomatic.sort_values(["queried_icd", "prct_fam_agree", "ccsr_1"], axis=0, ascending=[True, False, True],
               inplace=True, ignore_index=True)

    # failed (don't include closefam_failed here because some of those would have been mapped
    # automatically using distant family relationship!)
    failed = distfam_failed
    failed.sort_values(["queried_icd"], axis=0, ascending=True,
               inplace=True, ignore_index=True)

    return automatic, semiautomatic, failed


def get_closely_related(unmapped, ccsr, verbose):
    """Finds any closely related codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file.

    Close relatives are defined as `Children`, `Siblings`, or `Parents`.

    Parameters
    ----------
    unmapped : str
        ICD-10 code that could not be mapped directly.

    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        ==============  =================================================
        icd             ICD-10 codes (as `str`)
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

    verbose : bool
        If True, progress bars are printed.

    Returns
    -------
    related_df: pd.DataFrame
        All Children, Sibling, and Parent codes of the unmapped
        ICD-10 codes. Each row contains a unique combination of queried_icd
        and any closly related ICD-10 code in the official CCSR file.

        =============  ==================================================
        queried_icd    ICD-10 codes given in the `unmapped` input
                       (as `str`)
        relationship   The relationship that the related ICD-10 codes in
                       the official CCSR file have to `queried_icd` (i.e.,
                       "Close", as `str`)
        icd            Related ICD-10 code identified in official CCSR
                       file (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ==================================================

    """
    related_df = pd.DataFrame([])

    for func in [get_children, get_sibs, get_parents]:
        related = func(unmapped, ccsr)
        if related is not None:
            if related_df.empty:
                related_df = related
            else:
                related_df = pd.concat([related_df, related])

    return related_df


def get_children(icd, ccsr):
    """Finds any Children codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file. Children codes are
    defined as ICD-10 codes in the official CCSR mapping file that contain the
    queried ICD-10 code, but have one or more additional characters.
    For example, “A4181” is a Child of “A418”.

    Parameters
    ----------
    icd : str 
        ICD-10 code that could not be mapped directly.

    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =======================================
        icd            ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =======================================

    Returns
    -------
    related: pd.DataFrame
        All Children codes of the unmapped ICD-10 codes and the CCSR categories of
        each identified Child. Each row corresponds to one Child code.

        =============  ==============================================
        queried_icd    The queried ICD-10 codes given in `icd`.
        relationship   Relationship to `queried_icd` (i.e.,
                       "Children", as `str`)
        icd            Children ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ==============================================

    """
    child = ccsr[ccsr['icd'].str.startswith(icd)]
    if len(child) == 0:
        return None
    for gen_num in range(1, 5):
        generation = child[child['icd'].str.len() == len(icd) + gen_num]
        if len(generation) > 0:
            related = generation.drop(columns=['ccsr_def'])
            related.insert(loc=0, column='relationship', value='Children')
            related.insert(loc=0, column='queried_icd', value=icd)
            return related
    return None


def get_sibs(icd, ccsr):
    """Finds any Sibling codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file. Siblings are defined
    as any ICD-10 codes that have the same number of characters but differ in
    their last digit. For example, “B485” and “B488” are Sibling codes.

    Parameters
    ----------
    icd : str 
        ICD-10 code that could not be mapped directly.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =======================================
        icd            ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =======================================

    Returns
    -------
    related: pd.DataFrame
        All Sibling codes of the unmapped ICD-10 codes and the CCSR categories of
        each identified Sibling. Each row corresponds to one Sibling code.

        =============  ==============================================
        queried_icd    The queried ICD-10 codes given in `icd`.
        relationship   Relationship to `queried_icd` (i.e.,
                       "Siblings", as `str`)
        icd            Sibling ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ==============================================

    """
    sibs = ccsr[ccsr['icd'].str[:-1] == icd[:-1]]
    if len(sibs) == 0:
        return None
    related = sibs.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='relationship', value='Siblings')
    related.insert(loc=0, column='queried_icd', value=icd)
    return related


def get_parents(icd, ccsr):
    """Finds any Parent codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file. Parent codes are
    defined as ICD-10 codes in the official CCSR mapping file that are
    contained within the queried ICD-10 code, but have one less character.
    For example, “C880” is a Parent code of “C8808".

    Parameters
    ----------
    icd : str 
        ICD-10 code that could not be mapped directly.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =======================================
        icd            ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =======================================

    Returns
    -------
    related: pd.DataFrame
        All Parent codes of the unmapped ICD-10 codes and the CCSR categories of
        each identified Parent. Each row corresponds to one Parent code.

        =============  ==============================================
        queried_icd    The queried ICD-10 codes given in `icd`.
        relationship   Relationship to `queried_icd` (i.e.,
                       "Parents", as `str`)
        icd            Parent ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ==============================================

    """
    for str_len in range(len(icd) - 1, 2, -1):
        generation = ccsr[ccsr['icd'] == icd[:str_len]]
        if len(generation) > 0:
            related = generation.drop(columns=['ccsr_def'])
            related.insert(loc=0, column='relationship', value='Parents')
            related.insert(loc=0, column='queried_icd', value=icd)
            return related
    return None



def get_distantly_related(unmapped, ccsr, verbose):
    """Finds any distantly related codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file.

    Distant relatives are defined as `Half-Siblings`, `Cousins`, or `Extended Family`.

    Parameters
    ----------
    unmapped : str
        ICD-10 code that could not be mapped directly.

    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        ==============  =================================================
        icd             ICD-10 cods (as `str`)
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

    verbose : bool
        If True, progress bars are printed.

    Returns
    -------
    related_df: pd.DataFrame
        All Half-Siblings, Cousins, and Extended Family member codes of the
        unmapped ICD-10 codes. Each row contains a unique combination of
        `queried_icd` and any distantly related ICD-10 codes in the official
        CCSR file.

        =============  ==================================================
        queried_icd    ICD-10 codes given in the `unmapped` input
                       (as `str`)
        relationship   The relationship that the related ICD-10 codes in
                       the official CCSR file have to `queried_icd` (i.e.,
                       "Distant", as `str`)
        icd            Related ICD-10 codes identified in official CCSR
                       file (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ==================================================

    """

    related_df = pd.DataFrame([])

    for func in [get_halfsibs,get_cousins,get_extfam]:
        related = func(unmapped, ccsr)
        if related is not None:
            if related_df.empty:
                related_df = related
            else:
                related_df = pd.concat([related_df, related])

    return related_df


def get_halfsibs(icd, ccsr):
    """Finds any Half-Sibling codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file. Half-Siblings are
    defined as codes with the same number of characters that can differ
    on their last two digits as long as 1) the first three characters are
    identical and 2) the last two digits only differ by a distance of +/- 9.
    For example, “E1165” is a Half-Sibling of “E1170”.

    Parameters
    ----------
    icd : str 
        ICD-10 code that could not be mapped directly.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =======================================
        icd            ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =======================================

    Returns
    -------
    related: pd.DataFrame
        All Half-Sibling codes of the unmapped ICD-10 codes and the CCSR
        categories of each identified Half-Sibling. Each row corresponds to one
        Half-Sibling code.

        =============  ===================================================
        queried_icd    The queried ICD-10 codes given in `icd`.
        relationship   Relationship to `queried_icd` (i.e., "Half-Siblings",
                       as `str`)
        icd            Half-Sibling ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ===================================================

    """
    halfsibs = pd.DataFrame([])
    
    # check whether last 2 digits are within distance of +/- 9 of each other 
    # (only if code has at least 5 characters)
    if len(icd) >= 5:
        # find codes with matching first characters (at least 3) + same number of characters
        halfsibs = ccsr[(ccsr['icd'].str[:-2] == icd[:-2]) & (ccsr['icd'].str.len() == len(icd))]
        # check whether last 2 characters can be converted to integers
        halfsibs = halfsibs[halfsibs['icd'].str.slice(-2).str.isdigit()] 

        if len(halfsibs) > 0: # make sure last 2 characters can be converted to integers
            halfsibs = halfsibs[abs(halfsibs['icd'].str.slice(-2).astype(int) - int(icd[-2:])) < 10]

    if len(halfsibs) == 0:
        return None
    related = halfsibs.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='relationship', value='Half-Siblings')
    related.insert(loc=0, column='queried_icd', value=icd)
    return related


def get_cousins(icd, ccsr):
    """Finds any Cousin codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file. Cousins are defined
    as any ICD-10 codes that share the same first three characters, regardless
    of the remaining characters. For example, “F010” and “F0151” are Cousin
    codes.

    Parameters
    ----------
    icd : str 
        ICD-10 code that could not be mapped directly.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =======================================
        icd            ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =======================================

    Returns
    -------
    related: pd.DataFrame
        All Cousin codes of the unmapped ICD-10 codes and the CCSR categories of
        each identified Cousin. Each row corresponds to one Cousin code.

        =============  ==============================================
        queried_icd    The queried ICD-10 codes given in `icd`.
        relationship   Relationship to `queried_icd` (i.e.,
                       "Cousins", as `str`)
        icd            Cousin ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ==============================================

    """
    cousins = pd.DataFrame([])

    # find codes with matching first 3 characters 
    cousins = ccsr[(ccsr['icd'].str[:3] == icd[:3])]

    if len(cousins) == 0:
        return None
    related = cousins.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='relationship', value='Cousins')
    related.insert(loc=0, column='queried_icd', value=icd)

    return related


def get_extfam(icd, ccsr):
    """Finds any Extended Family codes of a given ICD-10 code and returns their
    CCSR categories from the official CCSR mapping file. Extended Family
    members are defined as any diagnosis codes that share the first two
    characters, regardless of any remaining characters. For example, “A970”
    and “A91" are Extended Family codes.

    Parameters
    ----------
    icd : str
        ICD-10 code that could not be mapped directly.
    ccsr : pd.DataFrame
        DataFrame containing the official mappings published by CCSR.
        Must have the following columns:

        =============  =================================
        icd            ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================

    Returns
    -------
    related: pd.DataFrame
        All Extended Family member codes of the unmapped ICD-10 codes and the
        CCSR categories of each identified Extended Family member. Each row
        corresponds to one Extended Family member.

        =============  ==============================================
        queried_icd    The queried ICD-10 codes given in `icd`.
        relationship   Relationship to `queried_icd` (i.e.,
                       "Extended Family", as `str`)
        icd            Extended Family member ICD-10 codes (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  ==============================================

    """
    extfam = pd.DataFrame([])

    # find codes with matching first 3 characters 
    extfam = ccsr[(ccsr['icd'].str[:2] == icd[:2])]

    if len(extfam) == 0:
        return None
    related = extfam.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='relationship', value='Extended Family')
    related.insert(loc=0, column='queried_icd', value=icd)

    return related
