from gemini_ccsr import relation_finder
from gemini_ccsr import formatter
import pandas as pd


def map_icd_to_ccsr(query_icd, official_ccsr, verbose=True):

    """Tries to predict the CCSR mapping of each ICD-10 code.

    If a diagnosis code is in the `official_ccsr` dataframe, then its CCSR mapping
    is returned in the `direct` DataFrame.

    If the diagnosis code is not found in the `official_ccsr` dataframe, the
    algorithm first checks for closely related codes (`Children`, `Siblings`,
    or `Parents`) with known CCSR mappings. If no close relatives
    are found, the algorithm checks for distantly related codes (`Half-siblings`,
    `Cousins`, or `Extended family`).

    If no close/distant relatives are found, the diagnosis code is returned in
    the `failed` DataFrame and needs to be mapped manually.

    If a diagnosis code has close/distant relatives with known CCSR
    mappings but none of the CCSR categories are shared by *all* identified
    family members, then the code is returned in the `semiautomatic` DataFrame
    (along with the percentage of family members that share each candidate
    CCSR category).

    If a diagnosis code has close/distant relatives all family members have
    one or more categories in common, then that code is mapped to all shared
    categories and returned in the `automatic` DataFrame.


    Parameters
    ----------
    query_icd : list
        A list containing the ICD-10 codes that should be mapped.
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
    direct : pd.DataFrame
        Mapped CCSR categories of ICD-10 codes that could be mapped directly.
        Returns the corresponding rows from the offical CCSR file. Has the
        following columns:

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

    automatic : pd.DataFrame
        Predicted CCSR categories for ICD-10 codes that could not be mapped directly,
        but whose CCSR categorization could be inferred based on related codes.
        Has the following columns:

        =====================  =========================================
        queried_icd            ICD-10 codes that were mapped automatically (as `str`)
        deciding_relationship  The relationship that the related ICD-10 codes in
                               `official_ccsr` have to the queried_icd (as `str`)
        related_codes          A list of all ICD-10 codes that were found in
                               `official_ccsr` and have the `deciding_relationship`
                               to `queried_icd` (as `list`)
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

    semiautomatic: pd.DataFrame
        Predicted CCSR categories for ICD-10 codes that could not be mapped
        directly or automatically. These are diagnosis codes for which the
        algorithm identified related codes, but none of the CCSR categories
        are shared by all related codes (i.e., CCSR mapping could not be
        inferred automatically). Has one row for each [ICD-10 code, candidate
        CCSR] combination. Additionally provides the percentage of related
        codes that share each predicted CCSR category. Users need to review
        the output file to exclude any rows with incorrect predictions. As
        opposed to automatically mapped codes, semi-automatic codes are
        returned without default CCSR category. Users need to carefully inspect
        the smeiautomatic output and choose a default CCSR category after
        validating the predicted CCSR categories. Has the following columns:

        ===============  =====================================================
        queried_icd      ICD-10 codes that were mapped semi-automatically
                         (as `str`)
        relationship     The type of relationship (`Close`/`Distant`) that the
                         related ICD-10 codes in `official_ccsr` have to the
                         `queried_icd` (as `str`)
        pred_ccsr        Predicted CCSR category (as `str`)
        pred_ccsr_desc   Predicted CCSR category description (as `str`)
        prct_fam_agree   Percentage of related diagnosis codes in the official
                         CCSR file that share the predicted CCSR category
                         (as `num`)
        ===============  =====================================================

    failed : pd.DataFrame
        The items of query_icd corresponding to ICD-10 codes that do not have
        any closely or distantly related codes in the official CCSR file. Only
        contains a single column for the failed ICD-10 codes.

        ===============  =====================================================
        queried_icd      Failed ICD-10 codes (as `str`)
        ===============  =====================================================

    """
    official_ccsr = formatter.check_ccsr(official_ccsr)
    query_icd = formatter.check_icd(query_icd)
    # 1) Identify direct mappings -> return anything else as unmapped
    direct, unmapped = relation_finder.get_direct_unmapped(
        query_icd, official_ccsr)
    # 2) Find codes in official CCSR file that are (closely/distantly) related to unmapped codes
    if not unmapped.empty:  # only if there are any codes that couldn't be mapped directly
        automatic, semiautomatic, failed = relation_finder.get_predicted(
            unmapped, official_ccsr, verbose)
        # For automatic codes: Add default CCSR category based on existing combinations of CCSR1-6 in CCSR file
        # if combination does not exist, use CCSR1 as default
        if not automatic.empty:
            automatic = formatter.add_default(automatic, official_ccsr)
            automatic = formatter.add_descs(automatic, official_ccsr, True)
        if not semiautomatic.empty:
            semiautomatic = formatter.add_descs(semiautomatic, official_ccsr, False)
    else:  # return empty data frame if all codes could be mapped directly
        automatic = semiautomatic = failed = pd.DataFrame([])

    return direct, automatic, semiautomatic, failed
