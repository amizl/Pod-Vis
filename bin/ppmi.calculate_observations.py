#!/usr/bin/env python3

"""

"""

import argparse
import re
import sys
import pandas as pd
import numpy as np
import pprint
import datetime as dt

scale_file_map = {'Semantic Fluency' : "Semantic_Fluency.csv",
                   'Benton Judgement of Line' : "Benton_Judgment_of_Line_Orientation.csv",
                   'MDS-UPDRS1-1' : "MDS_UPDRS_Part_I.csv",
                   'MDS-UPDRS1-2' : "MDS_UPDRS_Part_I__Patient_Questionnaire.csv",
                   'MDS-UPDRS2' : "MDS_UPDRS_Part_II__Patient_Questionnaire.csv",
                   'MDS-UPDRS3' : "MDS_UPDRS_Part_III.csv",
                   'Montreal Cognitive Assessment': "Montreal_Cognitive_Assessment__MoCA_.csv",
                   'Letter Number Sequencing': "Letter_-_Number_Sequencing__PD_.csv",
                   'Hopkins Verbal Learning Test': "Hopkins_Verbal_Learning_Test.csv",
                   'Epworth Sleepiness Scale': 'Epworth_Sleepiness_Scale.csv',
                   'Modified Schwab England ADL': 'Modified_Schwab_+_England_ADL.csv',
                   'SCOPA_AUT': 'SCOPA-AUT.csv',
                   'Symbol Digit Modalities': 'Symbol_Digit_Modalities.csv',
                   'State Trait Anxiety Inventory': 'State-Trait_Anxiety_Inventory.csv',
                   'Geriatric Depression': 'Geriatric_Depression_Scale__Short_.csv',
                   'REM Sleep Disorder': 'REM_Sleep_Disorder_Questionnaire.csv'
                   }
study_map = {}
patient_map = {}
subject_attr_map = {}
project_id = 1
pp = pprint.PrettyPrinter(indent=4)

# Take the multiple values for the APPRDX field and assign a study name
def assign_study(study_int):
    if study_int == 1:
        return "Parkinson's Disease"
    elif study_int == 2:
        return "Healthy Controls"
    elif study_int == 3:
        return "SWEDD"
    elif study_int == 4:
        return "Prodormal"
    elif study_int == 5 or study_int == 6:
        return "Genetic Cohort"
    elif study_int == 7 or study_int == 8:
        return "Genetic Registry"
    else:
        return "Unknown"

# Take the multiple columns designated for race and assign a sinlge race string
def assign_race(row):
    # RAINDALS, RAASIAN, RABLACK, RAHAWOPI, RAWHITE, RANOS.  Other = RAINDALS, RAHAWOPI, RANOS, or more than one race specified.
    if (np.sum(row) > 1):
        return "Multi"
    else:
        if (row['RAINDALS'] == 1):
            return "Other"
        elif (row['RAASIAN'] == 1):
            return 'Asian'
        elif (row['RABLACK'] == 1):
            return 'Black'
        elif (row['RAWHITE'] == 1):
            return 'White'
        elif (row['RANOS'] == 1):
            return 'Other'
        elif (row['RAHAWOPI'] == 1):
            return 'Other'
        else:
            return "Unknown"

def process_demographics(input_dir):

    # Enrolled PD Subject	- PATNO, APPRDX, ENROLLDT.  Merge SCREEN with RANDOM and find each unique PATNO with APPRDX = '1' that is not missing ENROLLDT.
    # Enrolled Healthy Control - 	PATNO, APPRDX, ENROLLDT.  Merge SCREEN with RANDOM and find each unique PATNO with APPRDX = '2' that is not missing ENROLLDT.
    # Enrolled SWEDD Subject - PATNO, APPRDX, ENROLLDT.  Merge SCREEN with RANDOM and find each unique PATNO with APPRDX = '3' that is not missing ENROLLDT.
    # Enrolled Prodromal Subject - PATNO, APPRDX, ENROLLDT.  Merge SCREEN with RANDOM and find each unique PATNO with APPRDX = '4' that is not missing ENROLLDT.
    # Enrolled Genetic Cohort Subject - PATNO, APPRDX, ENROLLDT.  Merge SCREEN with RANDOM and find each unique PATNO with APPRDX = '5' (PD subjects) or '6' (Unaffected subjects) that is not missing ENROLLDT.
    # Enrolled Genetic Registry Subject - PATNO, APPRDX, ENROLLDT.  Merge SCREEN with RANDOM and find each unique PATNO with APPRDX = '7' (PD subjects) or '8' (Unaffected subjects) that is not missing ENROLLDT.

    demographics_filename = 'Screening___Demographics.csv'
    features_filename = 'PD_Features.csv'
    randomization_filename = 'Randomization_table.csv'

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(input_dir + demographics_filename)
    df_features = pd.read_csv(input_dir + features_filename)
    df_random = pd.read_csv(input_dir + randomization_filename)

    # Subset the frame for the columns needed
    df_demo = df_demo.loc[:, ['PATNO', "APPRDX","CURRENT_APPRDX", "HISPLAT","RAINDALS","RAASIAN","RABLACK", "RAHAWOPI","RAWHITE","RANOS"]]
    df_random = df_random.loc[:, ["PATNO", "ENROLLDT", "BIRTHDT", "GENDER"]]
    df_features = df_features.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "SXMO","SXYEAR","PDDXDT","PDDXEST","DXTREMOR",
                                            "DXRIGID","DXBRADY","DXPOSINS","DXOTHSX","DXOTHCM","DOMSIDE"]]

    # Merge the demographics and randomization table to get study groups
    df_demo = df_demo.merge(df_random, how="outer", on = ['PATNO'])

    # Features file has multiple entries and all we need is diagnosis date, so just get one entry per subject
    # and the merge it with the demographics frame
    df_features = df_features.groupby(['PATNO']).first().reset_index()
    df_demo = df_demo.merge(df_features.loc[:, ['PATNO', "PDDXDT"]], how="outer", on = ['PATNO'])

    # Recode some of the variables such as gender, race
    df_demo['Study'] = df_demo['APPRDX'].apply(assign_study)
    df_demo['Race'] = df_demo[["RAINDALS","RAASIAN","RABLACK", "RAHAWOPI","RAWHITE","RANOS"]].apply(assign_race, axis = 1)
    df_demo['GENDER'] = df_demo['GENDER'].map(lambda x: 'Male' if x == 2 else 'Female')

    # Process some of the dates to assume the first of the month allow date operations
    # and then convert the datetime string to date
    df_demo[['ENROLLDT', 'BIRTHDT', 'PDDXDT']] = df_demo[['ENROLLDT', 'BIRTHDT', 'PDDXDT']].apply(lambda x: "1/" + x)
    df_demo[['ENROLLDT', 'BIRTHDT', 'PDDXDT']] = df_demo[['ENROLLDT', 'BIRTHDT', 'PDDXDT']].apply(lambda x: pd.to_datetime(x, format='%d/%m/%Y', errors='coerce'))

    # Calculate some of the numeric properties such as age at enrollemnt, age at diagnosis
    df_demo['enroll_age'] = round((df_demo['ENROLLDT'] - df_demo['BIRTHDT']).dt.days/365.25, 1) 
    df_demo['pd_diagnosis_age'] = round((df_demo['PDDXDT'] - df_demo['BIRTHDT']).dt.days/365.25, 1 )

    # Remove some of the unwanted columns from the demographic variables
    df_demo = df_demo.loc[:, ['PATNO', 'Study', 'Race', 'BIRTHDT', 'GENDER', 'enroll_age', 'pd_diagnosis_age',
                                "APPRDX","CURRENT_APPRDX", 'ENROLLDT', 'PDDXDT']]
    pp.pprint(df_demo)
    return df_demo


def process_semantic_fluency(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['semantic_fluency'] = df.loc[:, ['VLTANIM', 'VLTVEG', 'VLTFRUIT']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'semantic_fluency']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df

def process_benton_judgement(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    pp.pprint(df)
    df['benton_judgement'] = df.loc[:, ["JLO_TOTCALC"]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'benton_judgement']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df

def process_mds_updrs_1_1(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_1_1'] = df.loc[:, ['NP1COG', 'NP1HALL', 'NP1DPRS', 'NP1ANXS', 'NP1APAT','NP1DDS']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'mds_updrs_1_1']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df

def process_mds_updrs_1_2(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_1_2'] = df.loc[:, ["NP1SLPN", "NP1SLPD", "NP1PAIN", "NP1URIN", "NP1CNST", "NP1LTHD", "NP1FATG"]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'mds_updrs_1_2']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df            

def process_mds_updrs_2(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_2'] = df.loc[:, ["NUPSOURC","NP2SPCH","NP2SALV","NP2SWAL","NP2EAT","NP2DRES","NP2HYGN","NP2HWRT","NP2HOBB",
                                    "NP2TURN","NP2TRMR","NP2RISE","NP2WALK","NP2FREZ"]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'mds_updrs_2']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df

def process_mds_updrs_3(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_3'] = df.loc[:, ["NP3SPCH","NP3FACXP","NP3RIGN","NP3RIGRU","NP3RIGLU","PN3RIGRL","NP3RIGLL","NP3FTAPR","NP3FTAPL","NP3HMOVR",
                                    "NP3HMOVL","NP3PRSPR","NP3PRSPL","NP3TTAPR","NP3TTAPL","NP3LGAGR","NP3LGAGL","NP3RISNG","NP3GAIT","NP3FRZGT",
                                    "NP3PSTBL","NP3POSTR","NP3BRADY","NP3PTRMR","NP3PTRML","NP3KTRMR","NP3KTRML","NP3RTARU","NP3RTALU","NP3RTARL",
                                    "NP3RTALL","NP3RTALJ","NP3RTCON"
                                    ]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'mds_updrs_3']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df

def process_moca(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'MCATOT']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df

def process_lns(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'LNS_TOTRAW']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    

def process_hvlt(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'DVT_TOTAL_RECALL', 'DVT_DELAYED_RECALL', 'DVT_RETENTION']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    

def process_ess(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['ESS_TOT'] = df.loc[:, ["ESS1","ESS2","ESS3","ESS4","ESS5","ESS6","ESS7","ESS8"]].sum(axis=1, skipna = False)
    df['ESS'] = np.where(df.ESS_TOT >= 10, "Sleepy", "Not Sleepy")
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'ESS_TOT', 'ESS']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    

def process_mse_adl(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'MSEADLG']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    

def process_scopa_aut(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "SCAU1","SCAU2","SCAU3","SCAU4","SCAU5","SCAU6","SCAU7","SCAU8","SCAU9","SCAU10",
                    "SCAU11","SCAU12","SCAU13","SCAU14","SCAU15","SCAU16","SCAU17","SCAU18","SCAU19","SCAU20",
                    "SCAU21","SCAU22","SCAU23","SCAU23A","SCAU23AT","SCAU24","SCAU25"]]

    # Compute the first 21 values but replave 9 with 3 as that is the formula specified in the conversion document
    # SCAU1 - SCAU25.  For questions 1-21 (SCAU1 - SCAU21), add 3 points for each response of "9". Otherwise, add the number of points in response.  
    # For questions 22-25 (SCAU22 - SCAU25), add 0 points for each response of "9". Otherwise, add the number of points in response.
    df_part1 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "SCAU1","SCAU2","SCAU3","SCAU4","SCAU5","SCAU6","SCAU7","SCAU8","SCAU9","SCAU10",
                    "SCAU11","SCAU12","SCAU13","SCAU14","SCAU15","SCAU16","SCAU17","SCAU18","SCAU19","SCAU20",
                    "SCAU21"]]
    df_part1 = df_part1.where(df_part1 != 9, other = 3)
    df_part1['part_1'] = df_part1.loc[:, ["SCAU1","SCAU2","SCAU3","SCAU4","SCAU5","SCAU6","SCAU7","SCAU8","SCAU9","SCAU10",
                    "SCAU11","SCAU12","SCAU13","SCAU14","SCAU15","SCAU16","SCAU17","SCAU18","SCAU19","SCAU20",
                    "SCAU21"]].sum(axis=1, skipna = False)
    
    df_part2 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "SCAU22","SCAU23","SCAU23A","SCAU23AT","SCAU24","SCAU25"]]
    df_part2 = df_part2.where(df_part2 != 9, other = 0)
    df_part2['part_2'] = df_part2.loc[:, ["SCAU22","SCAU23","SCAU23A","SCAU23AT","SCAU24","SCAU25"]].sum(axis=1, skipna = False)
    df_part1 = df_part1.merge(df_part2, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    df = df_part1.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'part_1', 'part_2']]
    df['SCOPA-AUT'] = df.loc[:, ['part_1', 'part_2']].sum(axis=1, skipna = False)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'SCOPA-AUT']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    

def process_sdm(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'SDMTOTAL']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    

# Reverse the score by subtracting value from 5
def stai_reverse_score(value):
    value = 5 - value
    return value

def process_stai(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "STAIAD1","STAIAD2","STAIAD3","STAIAD4","STAIAD5","STAIAD6","STAIAD7","STAIAD8","STAIAD9","STAIAD10",
                    "STAIAD11","STAIAD12","STAIAD13","STAIAD14","STAIAD15","STAIAD16","STAIAD17","STAIAD18","STAIAD19","STAIAD20",
                    "STAIAD21","STAIAD22","STAIAD23","STAIAD24","STAIAD25","STAIAD26","STAIAD27","STAIAD28","STAIAD29","STAIAD30",
                    "STAIAD31","STAIAD32","STAIAD33","STAIAD34","STAIAD35","STAIAD36","STAIAD37","STAIAD38","STAIAD39","STAIAD40"]]

    # STAIAD1 - STAIAD40.  Add values for the following questions:  3, 4, 6, 7, 9, 12, 13, 14, 17, 18, 22, 24, 25, 28, 29, 31, 32, 35, 37, 38, 40.  
    # Use reverse scoring for the remaining questions and add to the first score (e.g., if value = 1, add 4 points to score; if value = 2, add 3 points to score, etc).
    df_part1 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "STAIAD3","STAIAD4","STAIAD6","STAIAD7","STAIAD9",
                    "STAIAD12","STAIAD13","STAIAD14","STAIAD17","STAIAD18",
                    "STAIAD22","STAIAD24","STAIAD25","STAIAD28","STAIAD29",
                    "STAIAD31","STAIAD32","STAIAD35","STAIAD37","STAIAD38","STAIAD40"]]
    df_part1['part_1'] = df_part1.loc[:, ["STAIAD3","STAIAD4","STAIAD6","STAIAD7","STAIAD9",
                    "STAIAD12","STAIAD13","STAIAD14","STAIAD17","STAIAD18",
                    "STAIAD22","STAIAD24","STAIAD25","STAIAD28","STAIAD29",
                    "STAIAD31","STAIAD32","STAIAD35","STAIAD37","STAIAD38","STAIAD40"]].sum(axis=1, skipna = False)

    # For the part 2 variable flip the values by subtracting the value from 5
    df_part2 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "STAIAD1","STAIAD2","STAIAD5","STAIAD8","STAIAD10",
                    "STAIAD11","STAIAD15","STAIAD16","STAIAD19","STAIAD20",
                    "STAIAD21","STAIAD23","STAIAD26","STAIAD27","STAIAD30",
                    "STAIAD33","STAIAD34","STAIAD36","STAIAD39"]]
    df_part2[["STAIAD1","STAIAD2","STAIAD5","STAIAD8","STAIAD10",
                    "STAIAD11","STAIAD15","STAIAD16","STAIAD19","STAIAD20",
                    "STAIAD21","STAIAD23","STAIAD26","STAIAD27","STAIAD30",
                    "STAIAD33","STAIAD34","STAIAD36","STAIAD39"]] = df_part2[["STAIAD1","STAIAD2","STAIAD5","STAIAD8","STAIAD10",
                    "STAIAD11","STAIAD15","STAIAD16","STAIAD19","STAIAD20",
                    "STAIAD21","STAIAD23","STAIAD26","STAIAD27","STAIAD30",
                    "STAIAD33","STAIAD34","STAIAD36","STAIAD39"]].apply(lambda x: stai_reverse_score(x), axis = 1)
    df_part2['part_2'] = df_part2.loc[:, ["STAIAD1","STAIAD2","STAIAD5","STAIAD8","STAIAD10",
                    "STAIAD11","STAIAD15","STAIAD16","STAIAD19","STAIAD20",
                    "STAIAD21","STAIAD23","STAIAD26","STAIAD27","STAIAD30",
                    "STAIAD33","STAIAD34","STAIAD36","STAIAD39"]].sum(axis=1, skipna = False)

    df_part1 = df_part1.merge(df_part2, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    df = df_part1.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'part_1', 'part_2']]
    df['STAI'] = df.loc[:, ['part_1', 'part_2']].sum(axis=1, skipna = False)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'STAI']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    


def process_ger_dep(filename):
   # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "GDSSATIS","GDSDROPD","GDSEMPTY","GDSBORED","GDSGSPIR","GDSAFRAD","GDSHAPPY",
                    "GDSHLPLS","GDSHOME","GDSMEMRY","GDSALIVE","GDSWRTLS","GDSENRGY","GDSHOPLS","GDSBETER"]]

    # Add 1 point for each response of "No" (0) to any of the following variables:  GDSSATIS, GDSGSPIR, GDSHAPPY, GDSALIVE, GDSENRGY. 
    # Add 1 point for each response of "Yes" (1) to any of the following variables:  GDSDROPD, GDSEMPTY, GDSBORED, GDSAFRAD, GDSHLPLS, GDSHOME, GDSMEMRY, GDSWRTLS, GDSHOPLS, GDSBETER.  
    # Subjects with GDS >=5 are "Depressed".  Subjects with GDS <5 are "Not Depressed".
    df_part1 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "GDSSATIS","GDSGSPIR","GDSHAPPY", "GDSALIVE","GDSENRGY"]]
    df_part1 = df_part1.where(df_part1 != 0, other = 1)
    df_part1['part_1'] = df_part1.loc[:, ["GDSSATIS","GDSGSPIR","GDSHAPPY", "GDSALIVE","GDSENRGY"]].sum(axis=1, skipna = False)
    
    df_part2 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "GDSDROPD","GDSEMPTY","GDSBORED","GDSAFRAD",
                    "GDSHLPLS","GDSHOME","GDSMEMRY","GDSWRTLS","GDSHOPLS","GDSBETER"]]
    df_part2 = df_part2.where(df_part2 != 1, other = 1)
    df_part2['part_2'] = df_part2.loc[:, ["GDSDROPD","GDSEMPTY","GDSBORED","GDSAFRAD",
                    "GDSHLPLS","GDSHOME","GDSMEMRY","GDSWRTLS","GDSHOPLS","GDSBETER"]].sum(axis=1, skipna = False)
    df_part1 = df_part1.merge(df_part2, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    df = df_part1.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'part_1', 'part_2']]
    df['Dep_Score'] = df.loc[:, ['part_1', 'part_2']].sum(axis=1, skipna = False)
    df['Geriatric Depression State'] = np.where(df.Dep_Score >= 5, "Depressed", "Not Depressed")
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'Dep_Score', 'Geriatric Depression State']]    

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    

def process_rem_sleep(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "DRMVIVID","DRMAGRAC","DRMNOCTB","SLPLMBMV","SLPINJUR","DRMVERBL","DRMFIGHT",
                    "DRMUMV","DRMOBJFL","MVAWAKEN","DRMREMEM","SLPDSTRB","STROKE","HETRA",
                    "PARKISM","RLS","NARCLPSY","DEPRS","EPILEPSY","BRNINFM","CNSOTH","CNSOTHCM"]]

    # Add 1 point for each response of "Yes" (1) to any of the following variables:  DRMVIVID, DRMAGRAC, DRMNOCTB, SLPLMBMV, SLPINJUR, DRMVERBL, DRMFIGHT, DRMUMV, DRMOBJFL, MVAWAKEN, DRMREMEM, SLPDSTRB.  
    # Add 1 point if any of the following variables has a response of "Yes" (1):  STROKE, HETRA, PARKISM, RLS, NARCLPSY, DEPRS, EPILEPSY, BRNINFM, CNSOTH.  
    # If any of the previous variables are missing, then RBD score is missing.  Subjects with score >=5 are RBD Positive.  Subjects with score <5 are RBD Negative.
    df_part1 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "DRMVIVID","DRMAGRAC","DRMNOCTB","SLPLMBMV","SLPINJUR","DRMVERBL","DRMFIGHT",
                    "DRMUMV","DRMOBJFL","MVAWAKEN","DRMREMEM", "SLPDSTRB"]]
    df_part1[["DRMVIVID","DRMAGRAC","DRMNOCTB","SLPLMBMV","SLPINJUR","DRMVERBL","DRMFIGHT",
                    "DRMUMV","DRMOBJFL","MVAWAKEN","DRMREMEM", "SLPDSTRB"]] = df_part1[["DRMVIVID","DRMAGRAC","DRMNOCTB","SLPLMBMV","SLPINJUR","DRMVERBL","DRMFIGHT",
                    "DRMUMV","DRMOBJFL","MVAWAKEN","DRMREMEM", "SLPDSTRB"]].where(df_part1 == 1, other = 0)
    df_part1['part_1'] = df_part1.loc[:, ["DRMVIVID","DRMAGRAC","DRMNOCTB","SLPLMBMV","SLPINJUR","DRMVERBL","DRMFIGHT",
                    "DRMUMV","DRMOBJFL","MVAWAKEN","DRMREMEM", "SLPDSTRB"]].sum(axis=1, skipna = False)

    df_part2 = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', "STROKE","HETRA",
                    "PARKISM","RLS","NARCLPSY","DEPRS","EPILEPSY","BRNINFM","CNSOTH"]]
    df_part2[["STROKE","HETRA",
                    "PARKISM","RLS","NARCLPSY","DEPRS","EPILEPSY","BRNINFM","CNSOTH"]] = df_part2[["STROKE","HETRA",
                    "PARKISM","RLS","NARCLPSY","DEPRS","EPILEPSY","BRNINFM","CNSOTH"]].where(df_part2 == 1, other = 0)
    df_part2['part_2'] = df_part2.loc[:, ["STROKE","HETRA",
                    "PARKISM","RLS","NARCLPSY","DEPRS","EPILEPSY","BRNINFM","CNSOTH"]].sum(axis=1, skipna = False)

    df_part1 = df_part1.merge(df_part2, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    df = df_part1.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'part_1', 'part_2']]
    df['REM_RBD_Score'] = df.loc[:, ['part_1', 'part_2']].sum(axis=1, skipna = False)
    df['REM RBD State'] = np.where(df.REM_RBD_Score >= 5, "REM RBD Positive", "REM RBD Negative")
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'INFODT', 'REM_RBD_Score', 'REM RBD State']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['PATNO', 'EVENT_ID', 'INFODT']).first().reset_index()
    return df    


def main():
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='Path to an input directory from where to get files' )
    parser.add_argument('-o', '--output_file_prefix', type=str, required=True, help='Prefix to use for all the output files that will be generated' )
    args = parser.parse_args()
    
    # Process the demographic variables
    df_demo = process_demographics(args.input_dir)

    # Cycle through the scales and calculate the totals or any other transformations that need to be made
    for scale, filename in scale_file_map.items():
        if (scale == 'Semantic Fluency'):
            print("Processing Semantic Fluency")
            df_semantic_fluency = process_semantic_fluency(args.input_dir + filename)
            pp.pprint(df_semantic_fluency.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'Benton Judgement of Line'):
            print("Processing Benton Judgement of Line")
            df_benton_judgement = process_benton_judgement(args.input_dir + filename)
            pp.pprint(df_benton_judgement.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'MDS-UPDRS1-1'):
            print("Processing MDS-UPDRS1-1")
            df_mds_updrs1_1 = process_mds_updrs_1_1(args.input_dir + filename)
            pp.pprint(df_mds_updrs1_1.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'MDS-UPDRS1-2'):
            print("Processing MDS-UPDRS1-2")
            df_mds_updrs1_2 = process_mds_updrs_1_2(args.input_dir + filename)
            pp.pprint(df_mds_updrs1_2.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'MDS-UPDRS2'):
            print("Processing MDS-UPDRS2")
            df_mds_updrs2 = process_mds_updrs_2(args.input_dir + filename)
            pp.pprint(df_mds_updrs2.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'MDS-UPDRS3'):
            print("Processing MDS-UPDRS3")
            df_mds_updrs3 = process_mds_updrs_3(args.input_dir + filename)
            pp.pprint(df_mds_updrs3.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
            exit
        elif (scale == 'Montreal Cognitive Assessment'):
            print("Processing Montreal Cognitive Assessment")
            df_moca = process_moca(args.input_dir + filename)
            pp.pprint(df_moca.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'Letter Number Sequencing'):
            print("Processing Letter Number Sequencing")
            df_lns =  process_lns(args.input_dir + filename)
            pp.pprint(df_lns.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'Hopkins Verbal Learning Test'):
            print("Processing Hopkins Verbal Learning Test")
            df_hvlt =  process_hvlt(args.input_dir + filename)
            pp.pprint(df_hvlt.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'Epworth Sleepiness Scale'):
            print("Processing Epworth Sleepiness Scale")
            df_ess =  process_ess(args.input_dir + filename)
            pp.pprint(df_ess.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'Modified Schwab England ADL'):
            print("Processing Modified Schwab England ADL")
            df_mse_adl =  process_mse_adl(args.input_dir + filename)
            pp.pprint(df_mse_adl.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'SCOPA_AUT'):
            print("Processing SCOPA_AUT")
            df_scopa_aut =  process_scopa_aut(args.input_dir + filename)
            pp.pprint(df_scopa_aut.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'Symbol Digit Modalities'):
            print("Processing Symbol Digit Modalities")
            df_sdm =  process_sdm(args.input_dir + filename)
            pp.pprint(df_sdm.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'State Trait Anxiety Inventory'):
            print("Processing State Trait Anxiety Inventory")
            df_stai =  process_stai(args.input_dir + filename)
            pp.pprint(df_stai.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'Geriatric Depression'):
            print("Processing Geriatric Depression")
            df_ger_dep =  process_ger_dep(args.input_dir + filename)
            pp.pprint(df_ger_dep.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
        elif (scale == 'REM Sleep Disorder'):
            print("Processing REM Sleep Disorder")
            df_rem_sleep =  process_rem_sleep(args.input_dir + filename)
            pp.pprint(df_rem_sleep.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))


    # Process UPDRS by merging and adding across the three measures
    df_mds_updrs1 = df_mds_updrs1_1.merge(df_mds_updrs1_2, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    df_mds_updrs1['mds_updrs_1'] = df_mds_updrs1.loc[:, ["mds_updrs_1_1", "mds_updrs_1_2"]].sum(axis=1, skipna = False)
    pp.pprint(df_mds_updrs1)

    df_mds_updrs = df_mds_updrs1.merge(df_mds_updrs2, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT']).merge(df_mds_updrs3, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_mds_updrs)
    labels = ["mds_updrs_1", "mds_updrs_2", "mds_updrs_3"]
    pp.pprint(df_mds_updrs.loc[:, df_mds_updrs.columns.intersection(labels)])
    df_mds_updrs['mds_updrs_total'] = df_mds_updrs.loc[:, df_mds_updrs.columns.intersection(labels) ].sum(axis=1, skipna = False)
    pp.pprint(df_mds_updrs.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Merge al the dataframes to create a big matrix of observations
    df_all_vars = df_semantic_fluency

    df_all_vars = df_all_vars.merge(df_benton_judgement, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    labels = ["PATNO", 'EVENT_ID', 'INFODT', "mds_updrs_1", "mds_updrs_2", "mds_updrs_3", "mds_updrs_total"]
    df_all_vars = df_all_vars.merge(df_mds_updrs.loc[:, df_mds_updrs.columns.intersection(labels)], how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    df_all_vars_sorted = df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars_sorted)

    # Merge MOCA
    df_all_vars = df_all_vars.merge(df_moca, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Merge LNS
    df_all_vars = df_all_vars.merge(df_lns, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Merge HVLT
    labels = ["PATNO", 'EVENT_ID', 'INFODT', 'DVT_TOTAL_RECALL', 'DVT_DELAYED_RECALL', 'DVT_RETENTION']
    df_all_vars = df_all_vars.merge(df_hvlt.loc[:, df_hvlt.columns.intersection(labels)], how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Merge ESS
    labels = ["PATNO", 'EVENT_ID', 'INFODT', "ESS_TOT", "ESS"]
    df_all_vars = df_all_vars.merge(df_ess.loc[:, df_ess.columns.intersection(labels)], how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Merge MSE-ADL
    df_all_vars = df_all_vars.merge(df_mse_adl, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Merge SCOPA-AUT
    df_all_vars = df_all_vars.merge(df_scopa_aut, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
    
    # Merge SDM
    df_all_vars = df_all_vars.merge(df_sdm, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
    
    # Merge STAI
    df_all_vars = df_all_vars.merge(df_stai, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
    
    # Merge Geriatric Depression
    df_all_vars = df_all_vars.merge(df_ger_dep, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Merge REM Sleep Disorder
    df_all_vars = df_all_vars.merge(df_rem_sleep, how="outer", on = ['PATNO', 'EVENT_ID', 'INFODT'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))

    # Some times there seem to be multiple rows for the same event with different date. In such situations we are
    # arbitrarily deciding to use the last one that appears
    df_all_vars = df_all_vars.groupby(['PATNO', 'EVENT_ID']).last().reset_index()
    df_all_vars_sorted = df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT'])

    # Once the dataframes are created write the table to a CSV file
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID', 'INFODT']))
    filename = "ppmi_obs.csv"
    df_all_vars_sorted.to_csv(args.input_dir + filename, index = False)

    pp.pprint(df_demo.sort_values(by = ['PATNO', 'Study']))
    filename = "ppmi_demographics.csv"
    df_demo.to_csv(args.input_dir + filename, index = False)

if __name__ == '__main__':
    main()
