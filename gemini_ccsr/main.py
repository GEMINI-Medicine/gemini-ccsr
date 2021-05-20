from gemini_ccsr import relation_finder
from gemini_ccsr import formatter


def map_icd_to_ccsr(query_icd, official_ccsr, verbose=True):
    """Tries to predict the CCSR mapping of each ICD 10 code.

    If a code is in the official_ccsr dataframe, then its CCSR mapping
    is returned.

    If a code has no close relatives (ancestors, descendants, or
    siblings) with known CCSR mappings, then it is returned in the
    failed DataFrame.

    If it has ancestors, descedants, or siblings with known CCSR
    mappings but each of these groups' members have no CCSR category in
    common, then it is returned (along with information about each of
    its relatives) in the unresolved DataFrame.

    If it has ancestors, descendants, or siblings with known CCSR
    mappings and one of these groups' members have one or more
    categories in common, then that code is mapped to those categories
    and returned in the resolved DataFrame.


    Parameters
    ----------
    query_icd : array_like
        A one-dimensional array_like object containing the ICD10 codes
        that should be mapped.
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
        The rows of official_ccsr that correspond to the ICD 10 codes
        given in icd
    resolved : pd.DataFrame
        ICD 10 codes given in query_icd whose CCSR categorizations could
        be predicted based on their relatives.
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
        The ICD 10 codes given in query_icd whose CCSR categorization
        could not be inferred, but do have close relatives with an
        official CCSR categorization. Has one row for each (unpredicted
        ICD 10 code, close relative) combination.
        Has the following columns:

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
        The rows of query_icd corresponding to ICD 10 codes who have no
        close relatives.
    """
    official_ccsr = formatter.check_ccsr(official_ccsr)
    query_icd = formatter.check_icd(query_icd)
    direct, unmapped = relation_finder.get_direct_unmapped(
        query_icd, official_ccsr)
    resolved, unresolved, failed = relation_finder.get_predicted(
        unmapped, official_ccsr, verbose)
    resolved = formatter.add_default(resolved, official_ccsr)
    resolved = formatter.add_descs(resolved, official_ccsr)
    unresolved = formatter.add_descs(unresolved, official_ccsr)
    return direct, resolved, unresolved, failed
