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
        The icds of ccsr that correspond to the ICD 10 codes given in
        icd
    unmapped: pd.DataFrame
        The rows of icd whose entries do not appear in ccsr.
    """
    print('1) Getting direct mapping for existing codes in official CCSR.')
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

    If a code has no close relatives (children,
    parents, or siblings) or distant relatives (half-siblings, cousins,
    extended family) with known CCSR mappings, then it is returned in the 
    failed DataFrame. If it has close/distant relatives with known CCSR,
    mappings but each of these groups' members have no CCSR
    category in common, then it is returned (along with information
    about each of its relatives) in the unresolved DataFrame. If it has
    close/distant relatives with known CCSR mappings and one of these
    groups' members have one or more categories in common, then that code
    is mapped to those categories and returned in the resolved DataFrame.


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
        Related Codes  Related ICD codes that determined outcome 
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
       
         
    
    #%% PREDICTIONS BASED ON CLOSELY RELATED CODES
    ccsr_colnames = ['ccsr_{}'.format(i) for i in range(1, 6)]

    # Get codes that are unmapped after direct mapping
    related_close = unmapped.sort_values('icd')
    related_close[['Deciding Relationship', 'ccsr_1','ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6','Related Codes']] = None
        
    closefam_resolved = pd.DataFrame(columns = ['ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6','Deciding Relationship','Queried ICD','Related Codes'])
    closefam_unresolved = pd.DataFrame([])
    closefam_failed = pd.DataFrame(columns = ['Queried ICD'])

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
        
        #icd_related = check_closefam[check_closefam['Queried ICD'] == icd] # get related codes of queried ICD code
        resolved = False
        
        icd_relation_temp = pd.DataFrame([]) # keep track of all categories that occured among any close relatives
        
        if not icd_related.empty: # if any close relationships found
            for relation in ['Child', 'Sibling', 'Parent']:
                icd_relation = icd_related[icd_related['Relationship'] == relation]
                #print(len(icd_relation)) # number of children/sibl/parents
                if len(icd_relation) == 0: # check if close family member exists, if not, check next close family group
                    continue
                
                icd_relation_temp = pd.concat([icd_relation_temp,icd_relation]) # keep track of all categories that occured among any close relatives
                
                code_counts = icd_relation[
                    ccsr_colnames].stack().value_counts() 
                agreed_codes = code_counts[
                    code_counts == len(icd_relation)].index.to_list() # identify CCSR1-6 categories that match across all children/sibl/parent codes (CCSR categories don't need to be in same order)
                
                if agreed_codes:
                    agreed_codes.extend((6 - len(agreed_codes))*[None]) 

                    # Create new dataframe with resolved code
                    res = pd.DataFrame({'Queried ICD':icd,
                                        'Deciding Relationship': relation,
                                       'Related Codes': [list(icd_related.loc[icd_related['Relationship']==relation,'icd'].values)]})
                    
                    res.loc[0, ['ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6']] = agreed_codes

                    closefam_resolved = pd.concat([closefam_resolved, res])
                    
                    resolved = True
                    break
            
            if not resolved and not icd_relation_temp.empty: # if no category agreement found, get all unique categories and percentage of overlap across all relationships
                # for each category among any close family members, get percentage of shared
                code_perc = pd.Series(100*icd_relation_temp[ccsr_colnames].stack().value_counts()/len(icd_relation_temp)).to_frame(name = 'Prct_fam_agree') 
                code_perc['Queried ICD'] = icd
                # only keep top 6 predicted categories
                code_perc.sort_values(by=['Prct_fam_agree'], ascending=False)
                ## remove any that are shared among fewer than 5% of relatives
                code_perc.drop(code_perc[code_perc['Prct_fam_agree']<5].index, inplace = True) 
                #if len(code_perc) >= 6: # pick top 6 shared categories
                #    code_perc = code_perc[0:6] 
                
                if len(code_perc) == 0: # if no categories that are shared by at least 5% of related codes, return as failed
                    closefam_failed = pd.concat([closefam_failed,pd.DataFrame({'Queried ICD': [icd]})])
                else: # add any shared categories among related codes
                    code_perc['Relationships'] = 'Close' #code_perc.apply(lambda row: tuple(sorted(icd_related['Relationship'].drop_duplicates())), axis = 1)
                    closefam_unresolved = pd.concat([closefam_unresolved,code_perc])
        
        else: # if no close relationships found at all
            closefam_failed = pd.concat([closefam_failed,pd.DataFrame({'Queried ICD': [icd]})])
                

    
    if not closefam_unresolved.empty:
        closefam_unresolved = closefam_unresolved.reset_index(drop=False).rename(
            columns={'index': 'ccsr_1'}).loc[:,['Queried ICD','ccsr_1','Prct_fam_agree','Relationships']]
    

    
    #%% PREDICTIONS BASED ON DISTANTLY RELATED CODES

    distfam_resolved = pd.DataFrame(columns = ['ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6','Deciding Relationship','Queried ICD','Related Codes'])
    distfam_unresolved = pd.DataFrame([])
    distfam_failed = pd.DataFrame(columns = ['Queried ICD'])
    
    if not closefam_failed.empty:
    
        # Get codes that are still failed based on close family relationships and check for distant relationships
        #check_distfam = get_distantly_related(closefam_failed.rename(columns={'Queried ICD': 'icd'}), ccsr, verbose)
    
        related_dist = closefam_failed.sort_values('Queried ICD').rename(columns={'Queried ICD': 'icd'})
        related_dist[['Deciding Relationship', 'ccsr_1','ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6','Related Codes']] = None

        if verbose:
            print('3) Inferring mappings based on ICD codes\' distant relatives.')
            time.sleep(1)
            iterator = tqdm(related_dist['icd'])
        else:
            iterator = related_dist['icd']
    
    
    
        # loop through each unmapped ICD code and check agreement among distantly related codes' CCSR categories
        # starting with half-siblings, then cousins, then extended family
        for icd in iterator:
            
            icd_related = get_distantly_related(icd, ccsr, verbose) # get related codes of queried ICD code
            
            #icd_related = check_closefam[check_closefam['Queried ICD'] == icd] # get related codes of queried ICD code
            resolved = False
            
            icd_relation_temp = pd.DataFrame([]) # keep track of all categories that occured among any close relatives
            
            if not icd_related.empty: # if any distant relationships found
                for relation in ['Half-Sibling','Cousin','Extended Family']:
                    icd_relation = icd_related[icd_related['Relationship'] == relation]
                    #print(len(icd_relation)) # number of half-siblings/cousins/ext. fam.
                    if len(icd_relation) == 0: # check if distant family member exists, if not, check next distant family group
                        continue
                    
                    if icd_relation_temp.empty: # DIFFERENCE TO CLOSE RELATIONSHIPS: Only include categories from 'closest' distant family group (e.g., if half-siblings exist, only include those and ignore cousins/extended family)
                        icd_relation_temp = pd.concat([icd_relation_temp,icd_relation]) # keep track of all categories that occured among any distant relatives
                    
                    code_counts = icd_relation[
                        ccsr_colnames].stack().value_counts() 
                    agreed_codes = code_counts[
                        code_counts == len(icd_relation)].index.to_list() # identify CCSR1-6 categories that match across all half-siblings/cousins/ext. fam. codes (CCSR categories don't need to be in same order)
                    
                    if agreed_codes:
                        agreed_codes.extend((6 - len(agreed_codes))*[None]) 

                        # Create new dataframe with resolved code
                        res = pd.DataFrame({'Queried ICD':icd,
                                        'Deciding Relationship': relation,
                                       'Related Codes': [list(icd_related.loc[icd_related['Relationship']==relation,'icd'].values)]})
                    
                        res.loc[0, ['ccsr_1', 'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6']] = agreed_codes

                        
                        distfam_resolved = pd.concat([distfam_resolved, res])
                        
                        resolved = True
                        break                

                    
                if not resolved and not icd_relation_temp.empty: # if no category agreement found, get all unique categories and percentage of overlap across all relationships
                    # for each category among any distant family members, get percentage of shared
                    code_perc = pd.Series(100*icd_relation_temp[ccsr_colnames].stack().value_counts()/len(icd_relation_temp)).to_frame(name = 'Prct_fam_agree') 
                    code_perc['Queried ICD'] = icd
                    ## remove any that are shared among fewer than 5% of relatives
                    code_perc.drop(code_perc[code_perc['Prct_fam_agree']<5].index, inplace = True) 
                    #if len(code_perc) >= 6: # pick top 6 shared categories 
                    #    code_perc = code_perc[0:6] 
                    
                    if len(code_perc) == 0: # if no categories that are shared by at least 5% of related codes, return as failed
                        distfam_failed = pd.concat([distfam_failed,pd.DataFrame({'Queried ICD': [icd]})])
                    else: # add any found categories shared among related codes
                        code_perc['Relationships'] = 'Distant' #code_perc.apply(lambda row: tuple(sorted(icd_related['Relationship'].drop_duplicates())), axis = 1)
                        distfam_unresolved = pd.concat([distfam_unresolved,code_perc])
            
            else: # if no distant relationships found at all
                distfam_failed = pd.concat([distfam_failed,pd.DataFrame({'Queried ICD': [icd]})])
              
        
        if not distfam_unresolved.empty:
            distfam_unresolved = distfam_unresolved.reset_index(drop=False).rename(
                columns={'index': 'ccsr_1'}).loc[:,['Queried ICD','ccsr_1','Prct_fam_agree','Relationships']]
    

                      
    #%% MERGE CLOSELY/DISTANTLY RELATED & RESOLVED CODES, RETURN WITH UNRESOLVED & FAILED CODES
    #resolved = pd.DataFrame(columns = ['Queried ICD', 'Deciding Relationship', 'ccsr_1',
    #                    'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6','Related Codes'])
    resolved = pd.concat([closefam_resolved,
        distfam_resolved]).reset_index(drop=True)

    resolved = resolved[['Queried ICD', 'Deciding Relationship', 'ccsr_1',
                        'ccsr_2', 'ccsr_3', 'ccsr_4', 'ccsr_5', 'ccsr_6','Related Codes']]
    
    
    # unresolved
    unresolved = pd.DataFrame(columns = ['Queried ICD','ccsr_1','Prct_fam_agree','Relationships'])
    unresolved = pd.concat([unresolved,closefam_unresolved,
        distfam_unresolved]).reset_index(drop=True)
    
    # failed
    failed = distfam_failed # don't include closefam_failed here because some of those would have been resolved using distant family relationship(!)
    
    
    return resolved, unresolved, failed


def get_closely_related(unmapped, ccsr, verbose):
    """Finds the close relatives of each ICD 10 code.

    Close relatives are defined as children, siblings, or parents.

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
    related_df: pd.DataFrame
        The children, siblings, and parents of the unmapped
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
    related_df = pd.DataFrame([])
    
    for func in [get_children, get_sibs, get_parents]:
        related = func(unmapped, ccsr)
        if related is not None:
            if related_df.empty:
                related_df = related
            else:
                #related_df = related_df.append(related)
                related_df = pd.concat([related_df, related])
    
    return related_df


def get_children(icd, ccsr):
    """Finds the children of a given ICD 10 code.

    Parameters
    ----------
    icd : Series
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
        The children of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in icd.
        Relationship   "Child".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    descs = ccsr[ccsr['icd'].str.startswith(icd)]
    if len(descs) == 0:
        return None
    for gen_num in range(1, 5):
        generation = descs[descs['icd'].str.len() == len(icd) + gen_num]
        if len(generation) > 0:
            related = generation.drop(columns=['ccsr_def'])
            related.insert(loc=0, column='Relationship', value='Child')
            related.insert(loc=0, column='Queried ICD', value=icd)
            return related
    return None


def get_sibs(icd, ccsr):
    """Finds the siblings of a given ICD 10 code.

    Parameters
    ----------
    icd : Series
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
        Queried ICD    The ICD 10 code given in icd.
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
    sibs = ccsr[ccsr['icd'].str[:-1] == icd[:-1]]
    if len(sibs) == 0:
        return None
    related = sibs.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='Relationship', value='Sibling')
    related.insert(loc=0, column='Queried ICD', value=icd)
    return related


def get_parents(icd, ccsr):
    """Finds the parents of a given ICD 10 code.

    Parameters
    ----------
    icd : Series
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
        The parents of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in icd.
        Relationship   "Parent".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    for str_len in range(len(icd) - 1, 2, -1):
        generation = ccsr[ccsr['icd'] == icd[:str_len]]
        if len(generation) > 0:
            related = generation.drop(columns=['ccsr_def'])
            related.insert(loc=0, column='Relationship', value='Parent')
            related.insert(loc=0, column='Queried ICD', value=icd)
            return related
    return None



def get_distantly_related(unmapped, ccsr, verbose):
    """Finds the distant relatives of each ICD 10 code.

    Distant relatives are defined as half-siblings, cousins, or extended family.

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
        The half-siblings, cousins, and extended family of the unmapped
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
    
    
    related_df = pd.DataFrame([])
    
    for func in [get_halfsibs,get_cousins,get_extfam]:
        related = func(unmapped, ccsr)
        if related is not None:
            if related_df.empty:
                related_df = related
            else:
                #related_df = related_df.append(related)
                related_df = pd.concat([related_df, related])
    
    return related_df


def get_halfsibs(icd, ccsr):
    """Finds the half-siblings of a given ICD 10 code.

    Parameters
    ----------
    icd : Series
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
        The half-siblings of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in icd.
        Relationship   "Half-Sibling".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    halfsibs = pd.DataFrame([])
    
    # check whether last 2 digits are within distance of +/- 9 of each other (only if code has at least 5 characters)
    if len(icd) >= 5:
        # find codes with matching first characters (at least 3) + same number of characters
        halfsibs = ccsr[(ccsr['icd'].str[:-2] == icd[:-2]) & (ccsr['icd'].str.len() == len(icd))]
        halfsibs = halfsibs[halfsibs['icd'].str.slice(-2).str.isdigit()] # check whether last 2 characters can be converted to integers
        
        if len(halfsibs) > 0: # make sure last 2 characters can be converted to integers
            halfsibs = halfsibs[abs(halfsibs['icd'].str.slice(-2).astype(int) - int(icd[-2:])) < 10] 
    
    if len(halfsibs) == 0:
        return None
    related = halfsibs.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='Relationship', value='Half-Sibling')
    related.insert(loc=0, column='Queried ICD', value=icd)
    return related


def get_cousins(icd, ccsr):
    """Finds the cousins of a given ICD 10 code.

    Parameters
    ----------
    icd : Series
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
        The cousins of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in icd.
        Relationship   "Half-Sibling".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    cousins = pd.DataFrame([])
    
    # find codes with matching first 3 characters 
    cousins = ccsr[(ccsr['icd'].str[:3] == icd[:3])]
        
    if len(cousins) == 0:
        return None
    related = cousins.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='Relationship', value='Cousin')
    related.insert(loc=0, column='Queried ICD', value=icd)
    
    return related


def get_extfam(icd, ccsr):
    """Finds the extended family of a given ICD 10 code.

    Parameters
    ----------
    icd : Series
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
        The extended family members of the unmapped ICD 10 codes.

        =============  =================================================
        Queried ICD    The ICD 10 code given in icd.
        Relationship   "Half-Sibling".
        icd            ICD 10 code (as `str`)
        ccsr_1         CCSR category 1 (as `str`)
        ccsr_2         CCSR category 2 (as `str`)
        ccsr_3         CCSR category 3 (as `str`)
        ccsr_4         CCSR category 4 (as `str`)
        ccsr_5         CCSR category 5 (as `str`)
        ccsr_6         CCSR category 6 (as `str`)
        =============  =================================================

    """
    extfam = pd.DataFrame([])
    
    # find codes with matching first 3 characters 
    extfam = ccsr[(ccsr['icd'].str[:2] == icd[:2])]
        
    if len(extfam) == 0:
        return None
    related = extfam.drop(columns=['ccsr_def'])
    related.insert(loc=0, column='Relationship', value='Extended Family')
    related.insert(loc=0, column='Queried ICD', value=icd)
    
    return related
