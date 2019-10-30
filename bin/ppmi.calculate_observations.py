#!/usr/bin/env python3

"""

"""

import argparse
import re
import sys
import pandas as pd
import numpy as np
import pprint

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
                   'Modified Schwab England ADL': 'Modified_Schwab_+_England_ADL.csv'
                   }
study_map = {}
patient_map = {}
subject_attr_map = {}
project_id = 1
pp = pprint.PrettyPrinter(indent=4)

def process_semantic_fluency(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['semantic_fluency'] = df.loc[:, ['VLTANIM', 'VLTVEG', 'VLTFRUIT']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'semantic_fluency']]
    return df

def process_benton_judgement(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    pp.pprint(df)
    df['benton_judgement'] = df.loc[:, ["JLO_TOTCALC"]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'benton_judgement']]
    return df

def process_mds_updrs_1_1(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_1_1'] = df.loc[:, ['NP1COG', 'NP1HALL', 'NP1DPRS', 'NP1ANXS', 'NP1APAT','NP1DDS']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'mds_updrs_1_1']]
    return df

def process_mds_updrs_1_2(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_1_2'] = df.loc[:, ["NP1SLPN", "NP1SLPD", "NP1PAIN", "NP1URIN", "NP1CNST", "NP1LTHD", "NP1FATG"]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'mds_updrs_1_2']]
    return df            

def process_mds_updrs_2(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_2'] = df.loc[:, ["NUPSOURC","NP2SPCH","NP2SALV","NP2SWAL","NP2EAT","NP2DRES","NP2HYGN","NP2HWRT","NP2HOBB",
                                    "NP2TURN","NP2TRMR","NP2RISE","NP2WALK","NP2FREZ"]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'mds_updrs_2']]
    return df

def process_mds_updrs_3(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['mds_updrs_3'] = df.loc[:, ["NP3SPCH","NP3FACXP","NP3RIGN","NP3RIGRU","NP3RIGLU","PN3RIGRL","NP3RIGLL","NP3FTAPR","NP3FTAPL","NP3HMOVR",
                                    "NP3HMOVL","NP3PRSPR","NP3PRSPL","NP3TTAPR","NP3TTAPL","NP3LGAGR","NP3LGAGL","NP3RISNG","NP3GAIT","NP3FRZGT",
                                    "NP3PSTBL","NP3POSTR","NP3BRADY","NP3PTRMR","NP3PTRML","NP3KTRMR","NP3KTRML","NP3RTARU","NP3RTALU","NP3RTARL",
                                    "NP3RTALL","NP3RTALJ","NP3RTCON"
                                    ]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'mds_updrs_3']]
    return df

def process_moca(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'MCATOT']]
    return df

def process_lns(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'LNS_TOTRAW']]
    return df    

def process_hvlt(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'DVT_TOTAL_RECALL', 'DVT_DELAYED_RECALL', 'DVT_RETENTION']]
    return df    

def process_ess(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['ESS_TOT'] = df.loc[:, ["ESS1","ESS2","ESS3","ESS4","ESS5","ESS6","ESS7","ESS8"]].sum(axis=1, skipna = False)
    df['ESS'] = np.where(df.ESS_TOT >= 10, "Sleepy", "Not Sleepy")
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'ESS_TOT', 'ESS']]
    return df    

def process_mse_adl(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['PATNO', 'EVENT_ID', 'MSEADLG']]
    return df    



def main():
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='Path to an input directory from where to get files' )
    parser.add_argument('-o', '--output_file_prefix', type=str, required=True, help='Prefix to use for all the output files that will be generated' )
    args = parser.parse_args()

    # Cycle through the scales and calculate the totals or any other transformations that need to be made
    for scale, filename in scale_file_map.items():
        if (scale == 'Semantic Fluency'):
            print("Processing Semantic Fluency")
            df_semantic_fluency = process_semantic_fluency(args.input_dir + filename)
            pp.pprint(df_semantic_fluency)

        elif (scale == 'Benton Judgement of Line'):
            print("Processing Benton Judgement of Line")
            df_benton_judgement = process_benton_judgement(args.input_dir + filename)
            pp.pprint(df_benton_judgement)

        elif (scale == 'MDS-UPDRS1-1'):
            print("Processing MDS-UPDRS1-1")
            df_mds_updrs1_1 = process_mds_updrs_1_1(args.input_dir + filename)
            pp.pprint(df_mds_updrs1_1)

        elif (scale == 'MDS-UPDRS1-2'):
            print("Processing MDS-UPDRS1-2")
            df_mds_updrs1_2 = process_mds_updrs_1_2(args.input_dir + filename)
            pp.pprint(df_mds_updrs1_2)

        elif (scale == 'MDS-UPDRS2'):
            print("Processing MDS-UPDRS2")
            df_mds_updrs2 = process_mds_updrs_2(args.input_dir + filename)
            pp.pprint(df_mds_updrs2)

        elif (scale == 'MDS-UPDRS3'):
            print("Processing MDS-UPDRS3")
            df_mds_updrs3 = process_mds_updrs_3(args.input_dir + filename)
            pp.pprint(df_mds_updrs3)
        elif (scale == 'Montreal Cognitive Assessment-'):
            print("Processing MDS-UPDRS3")
            df_moca = process_moca(args.input_dir + filename)
            pp.pprint(df_moca)
        elif (scale == 'Letter Number Sequencing'):
            print("Processing Letter Number Sequencing")
            df_lns =  process_lns(args.input_dir + filename)
            pp.pprint(df_lns)
        elif (scale == 'Hopkins Verbal Learning Test'):
            print("Processing Hopkins Verbal Learning Test")
            df_hvlt =  process_hvlt(args.input_dir + filename)
            pp.pprint(df_hvlt)
        elif (scale == 'Epworth Sleepiness Scale'):
            print("Processing Epworth Sleepiness Scale")
            df_ess =  process_ess(args.input_dir + filename)
            pp.pprint(df_ess)
        elif (scale == 'Modified Schwab England ADL'):
            print("Processing Modified Schwab England ADL")
            df_mse_adl =  process_mse_adl(args.input_dir + filename)
            pp.pprint(df_mse_adl)


    # Process UPDRS by merging and adding across the three measures
    df_mds_updrs1 = df_mds_updrs1_1.merge(df_mds_updrs1_2, how="outer", on = ['PATNO', 'EVENT_ID'])
    df_mds_updrs1['mds_updrs_1'] = df_mds_updrs1.loc[:, ["mds_updrs_1_1", "mds_updrs_1_2"]].sum(axis=1, skipna = False)
    pp.pprint(df_mds_updrs1)

    df_mds_updrs = df_mds_updrs1.merge(df_mds_updrs2, how="outer", on = ['PATNO', 'EVENT_ID']).merge(df_mds_updrs3, how="outer", on = ['PATNO', 'EVENT_ID'])
    pp.pprint(df_mds_updrs)
    labels = ["mds_updrs_1", "mds_updrs_2", "mds_updrs_3"]
    pp.pprint(df_mds_updrs.loc[:, df_mds_updrs.columns.intersection(labels)])
    df_mds_updrs['mds_updrs_total'] = df_mds_updrs.loc[:, df_mds_updrs.columns.intersection(labels) ].sum(axis=1, skipna = False)
    pp.pprint(df_mds_updrs.sort_values(by = ['PATNO', 'EVENT_ID']))

    # Merge al the dataframes to create a big matrix of observations
    df_all_vars = df_semantic_fluency

    df_all_vars = df_all_vars.merge(df_benton_judgement, how="outer", on = ['PATNO', 'EVENT_ID'])
    pp.pprint(df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID']))

    labels = ["PATNO", "EVENT_ID", "mds_updrs_1", "mds_updrs_2", "mds_updrs_3", "mds_updrs_total"]
    df_all_vars = df_all_vars.merge(df_mds_updrs.loc[:, df_mds_updrs.columns.intersection(labels)], how="outer", on = ['PATNO', 'EVENT_ID'])
    df_all_vars_sorted = df_all_vars.sort_values(by = ['PATNO', 'EVENT_ID'])
    pp.pprint(df_all_vars_sorted)

    # Once the dataframe is created write the table to a CSV file
    filename = "ppmi_obs.csv"
    df_all_vars_sorted.to_csv(args.input_dir + filename, index = False)

if __name__ == '__main__':
    main()
