#!/usr/bin/env python3

"""
This script is used to parse the winnow data and extract the unique observation names,
and observations and generate the subject and observation ontology list, subject attributes,
visit observations, and subject summary files from the file. If there are any transformations
that need to be performed on the data, they are performed here.

"""

import argparse
import re
import sys
import pandas as pd
import numpy as np
import os
import pprint
import datetime as dt

scale_file_map = {'UPDRS I' : "UMDPD_data.csv",
                   'UPDRS II' : "UMDPD_data.csv",
                   'UPDRS III' : "UMDPD_data.csv",
                   'UPDRS IV' : "UMDPD_data.csv",
                   'UPDRS Total' : "UMDPD_data.csv",
                   'Depression T Score' : "UMDPD_data.csv",
                   'Anxiety T Score' : "UMDPD_data.csv",
                   'CIRS Total' : "UMDPD_data.csv",
                   'ADLs' : "UMDPD_data.csv",
                   'IADLs' : "UMDPD_data.csv",
                   'OARS Total' : "UMDPD_data.csv",
                   'MMSE' : "UMDPD_data.csv",
                   'Hoehn and Yahr Stage' : "UMDPD_data.csv"}

pp = pprint.PrettyPrinter(indent=4)

# Method to calculate the change and rate of change for each group passed as a dataframe
def calc_duration_change(group):
    sorted_group = group.sort_values(by = ['VisitDay'])
    #print("printing sorted group")
    pp.pprint(sorted_group)
    min_index = 0
    max_index = group.shape[0] - 1
    #print("printing third field")
    print(sorted_group.iloc[max_index, 1], sorted_group.iloc[min_index, 1])
    duration = round((sorted_group.iloc[max_index, 1] - sorted_group.iloc[min_index, 1])/365.25, 2)
    delta = sorted_group.iloc[max_index, 3] - sorted_group.iloc[min_index, 3]
    if (duration == 0):
        ds = pd.Series({'Duration': 0,
                        'Change': delta,
                        'ROC': 0}) 
        return ds

    # If the duration is valid then calculate ROC
    rate_of_change = round(delta / duration, 2)

    # print("Duration %4.2f change %8.2f ROC %8.2f" % (duration, delta, rate_of_change))
    ds = pd.Series({'Duration': duration,
                        'Change': delta,
                        'ROC': rate_of_change})
    #pp.pprint(ds)
    return ds

def assign_race(row):
    if (row['Race'] == 1):
        return "Black"
    elif (row['Race'] == 2):
        return "White"
    elif (row['Race'] == 3):
        return "Native American or Alaska Native"
    elif (row['Race'] == 4):
        return "Native Hawaiian or Pacific Islander"
    elif (row['Race'] == 5):
        return "Asian"
    elif (row['Race'] == 6):
        return "More than one race"
    else:
        return "Unknown Race"

def process_demographics(input_dir):

    data_filename = "UMDPD_data.csv"

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(os.path.join(input_dir, data_filename))

    df_demo = df_demo.loc[:, ['WinnowID', "agefirstvisit","PDdurationatfirstvisit", "daysfromfirstvisit","Gender", "Race"]]

    df_demo['Study'] = "UMD Parkinson's Disease Cohort"
    df_demo['Gender'] = df_demo['Gender'].map(lambda x: 'Male' if x == 1 else 'Female')
    df_demo['Race'] = df_demo[['Race']].apply(assign_race, axis = 1)

    # Calculate some of the numeric properties such as age at diagnosis, age at diagnosis
    df_demo['Age At Diagnosis'] = round((df_demo['agefirstvisit'] - df_demo['PDdurationatfirstvisit']), 0 )

    df_demo = df_demo.loc[:, ["WinnowID", "Gender", "Study", "Race", "Age At Diagnosis"]].drop_duplicates()

    df_demo = df_demo.rename(columns={"WinnowID": "SubjectNum", 
                            "Gender": "Sex"}, 
                            errors="raise")
    ##pp.pprint(df_demo)
    return df_demo

def process_UPDRS_I(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['UPDRS_I'] = df.loc[:, ['UPDRS_1', 'UPDRS_2', 'UPDRS_3', 'UPDRS_4']].sum(axis=1, skipna = False)  
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'UPDRS_I']]    
    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()

    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "UPDRS_I": "UPDRS I"}, 
                    errors="raise")  
    return df
    #pp.pprint(df)

def process_UPDRS_II(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['UPDRS_II'] = df.loc[:, ['UPDRS_5','UPDRS_6','UPDRS_7', 'UPDRS_8', 'UPDRS_9', 'UPDRS_10', 'UPDRS_11', 'UPDRS_12', 'UPDRS_13', 'UPDRS_14', 'UPDRS_15',
    'UPDRS_14', 'UPDRS_15', 'UPDRS_16', 'UPDRS_17']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'UPDRS_II']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "UPDRS_II": "UPDRS II"}, 
                            errors="raise")
    return df
    #pp.pprint(df)
    

def process_UPDRS_III(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    #### option 1 df = df.loc[:, ['Winnowid', 'Daysfromfirstvisit', 'UPDRS_PIII']]
    df = df.loc[:, ['UPDRS_Piii', 'WinnowID', 'daysfromfirstvisit']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "UPDRS_Piii": "UPDRS III"}, 
                            errors="raise")
    return df
    #pp.pprint(df)
    #exit()

def process_UPDRS_IV(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['UPDRS_IV'] = df.loc[:, ['UPDRS_32', 'UPDRS_33', 'UPDRS_34', 'UPDRS_35','UPDRS_36', 'UPDRS_37', 'UPDRS_38', 'UPDRS_39', 'UPDRS_40', 'UPDRS_41', 'UPDRS_42',]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['WinnowID','daysfromfirstvisit', 'UPDRS_IV']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "UPDRS_IV": "UPDRS IV"}, 
                            errors="raise")
    return df

def process_UPDRS_Total(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'UPDRS_T']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "UPDRS_T": "UPDRS Total"}, 
                            errors="raise")
    return df    

def process_Depression_T_Score(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'DEP_TSC']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "DEP_TSC": "Depression T Score"}, 
                            errors="raise")
    return df   

def process_Anxiety_T_Score(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'ANX_TSC']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "ANX_TSC": "Anxiety T Score"}, 
                            errors="raise")
    return df   
    #pp.pprint(df)
    #exit()

def process_CIRS_Total(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'CIRS_T']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "CIRS_T": "CIRS Total"}, 
                            errors="raise")
    return df   

def process_ADLs(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'OARS_A']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "OARS_A": "ADLs"}, 
                            errors="raise")
    return df   

def process_IADLs(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'OARS_I']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "OARS_I": "IADLs"}, 
                            errors="raise")
    return df   

def process_OARS_Total(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'OARS_T']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "OARS_T":"OARS Total"}, 
                            errors="raise")
    return df   

def process_MMSE(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'MMSE_RECODE']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay",
                            "MMSE_RECODE": "MMSE"}, 
                            errors="raise")
    return df     

 
def process_Hoehn_and_Yahr_Stage(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['WinnowID', 'daysfromfirstvisit', 'HYSTG']]

    df = df.groupby(['WinnowID', 'daysfromfirstvisit']).first().reset_index()
    df = df.rename(columns={"WinnowID": "SubjectNum", 
                            "daysfromfirstvisit": "VisitDay"}, 
                            errors="raise")
    return df   
    #pp.pprint(df)

def main():
    # Parse the arguments
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='Path to an input directory from where to get files' )
    parser.add_argument('-o', '--output_dir', type=str, required=False, help='Path to directory where the output files that will be generated' )
    args = parser.parse_args()

    # If the output dir is not specified then use the input dir
    if args.output_dir is None:
        args.output_dir = args.input_dir

    # Process the demographic variables
    df_demo = process_demographics(args.input_dir)
    df_demo_long = pd.melt(df_demo, id_vars=['SubjectNum'], var_name ='SubjectVar', value_name ='Value')
    df_demo_long = df_demo_long.dropna()

    # Cycle through the scales and calculate the totals or any other transformations that need to be made
    for scale, filename in scale_file_map.items():
        if (scale == 'UPDRS I'):
            print("Processing UPDRS I")
            df_UPDRS_I = process_UPDRS_I(os.path.join(args.input_dir, filename))
        elif (scale == 'UPDRS II'):
            print("Processing UPDRS II")
            df_UPDRS_II = process_UPDRS_II(os.path.join(args.input_dir, filename))
        elif (scale == 'UPDRS III'):
            print("Processing UPDRS III")
            df_UPDRS_III = process_UPDRS_III(os.path.join(args.input_dir, filename))
            # pp.pprint(df_mds_updrs1_1.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'UPDRS IV'):
            print("Processing UPDRS IV")
            df_UPDRS_IV = process_UPDRS_IV(os.path.join(args.input_dir, filename))
            # pp.pprint(df_mds_updrs1_1.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'UPDRS Total'):
            print("Processing UPDRS Total")
            df_UPDRS_Total = process_UPDRS_Total(os.path.join(args.input_dir, filename))
            # pp.pprint(df_mds_updrs1_2.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'Depression T Score'):
            print("Processing Depression T Score")
            df_Depression_T_Score = process_Depression_T_Score(os.path.join(args.input_dir, filename))
            # pp.pprint(df_mds_updrs2.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'Anxiety T Score'):
            print("Processing Anxiety T Score")
            df_Anxiety_T_Score = process_Anxiety_T_Score(os.path.join(args.input_dir, filename))
            # pp.pprint(df_mds_updrs3.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'CIRS Total'):
            print("Processing CIRS Total")
            df_CIRS_Total = process_CIRS_Total(os.path.join(args.input_dir, filename))
            # pp.pprint(df_moca.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'ADLs'):
            print("Processing ADLs")
            df_ADLs =  process_ADLs(os.path.join(args.input_dir, filename))
            # pp.pprint(df_lns.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'IADLs'):
            print("Processing IADLs")
            df_IADLs =  process_IADLs(os.path.join(args.input_dir, filename))
            # pp.pprint(df_hvlt.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'OARS Total'):
            print("Processing OARS Total")
            df_OARS_Total =  process_OARS_Total(os.path.join(args.input_dir, filename))
            # pp.pprint(df_ess.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'MMSE'):
            print("Processing MMSE")
            df_MMSE =  process_MMSE(os.path.join(args.input_dir, filename))
            # pp.pprint(df_mse_adl.sort_values(by = ['SubjectNum', 'VisitCode']))
        elif (scale == 'Hoehn and Yahr Stage'):
            print("Processing Hoehn and Yahr Stage")
            df_Hoehn_and_Yahr_Stage =  process_Hoehn_and_Yahr_Stage(os.path.join(args.input_dir, filename))

# Process UPDRS by merging and adding across the three measures
    df_UPDRS = df_UPDRS_I.merge(df_UPDRS_II, how="outer", on = ['SubjectNum', 'VisitDay'])
    pp.pprint(df_UPDRS)

    df_UPDRS = df_UPDRS.merge(df_UPDRS_III, how="outer", 
                                        on = ['SubjectNum', 'VisitDay']
                                       )
    pp.pprint(df_UPDRS)

    df_UPDRS = df_UPDRS.merge(df_UPDRS_IV, how="outer", 
                                        on = ['SubjectNum', 'VisitDay']
                                       )
    #pp.pprint(df_UPDRS)

    df_UPDRS = df_UPDRS.merge(df_UPDRS_Total, how="outer", 
                                        on = ['SubjectNum', 'VisitDay']
                                       )
    
    #pp.pprint(df_UPDRS)

    # Merge al the dataframes to create a big matrix of observations
    df_all_vars = df_Depression_T_Score

    df_all_vars = df_all_vars.merge(df_Anxiety_T_Score, how="outer", on = ['SubjectNum', 'VisitDay'])
    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode']))



    #pp.pprint(df_all_vars)
    #exit()


    labels = ["SubjectNum", 'VisitDay', "UPDRS I", "UPDRS II", "UPDRS III", "UPDRS IV", "UPDRS Total"]
    df_all_vars = df_all_vars.merge(df_UPDRS.loc[:, df_UPDRS.columns.intersection(labels)], how="outer", on = ['SubjectNum', 'VisitDay'])
    df_all_vars_sorted = df_all_vars.sort_values(by = ['SubjectNum', 'VisitDay'])
    # pp.pprint(df_all_vars_sorted)

    df_all_vars = df_all_vars.merge(df_CIRS_Total, how="outer", on = ['SubjectNum', 'VisitDay'])
    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode']))

    df_all_vars = df_all_vars.merge(df_ADLs, how="outer", on = ['SubjectNum', 'VisitDay'])
    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode']))

    df_all_vars = df_all_vars.merge(df_IADLs, how="outer", on = ['SubjectNum', 'VisitDay'])
    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode']))

    df_all_vars = df_all_vars.merge(df_OARS_Total, how="outer", on = ['SubjectNum', 'VisitDay'])
   
    df_all_vars = df_all_vars.merge(df_MMSE, how="outer", on = ['SubjectNum', 'VisitDay'])
   
    df_all_vars = df_all_vars.merge(df_Hoehn_and_Yahr_Stage, how="outer", on = ['SubjectNum', 'VisitDay'])

    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitDay']))

    # Get the unique visits for all the subjects and calculate visit number
    df_unique_sub_visits = df_all_vars.sort_values(['SubjectNum', 'VisitDay']).groupby(['SubjectNum', 'VisitDay']).last().reset_index().loc[:, ["SubjectNum", "VisitDay", "VisitDate"]]
    df_unique_sub_visits = df_unique_sub_visits.sort_values(['SubjectNum', 'VisitDay'])
    # pp.pprint(df_unique_sub_visits)
    df_unique_sub_visits['VisitNum'] = df_unique_sub_visits.groupby(['SubjectNum']).cumcount()+1
    df_unique_sub_visits['VisitCode'] = df_unique_sub_visits['VisitNum']

    date_time_str = '2000-01-01'
    date_time_obj = dt.datetime.strptime(date_time_str, '%Y-%m-%d')
    temp = df_unique_sub_visits['VisitDay'].apply(np.ceil).apply(lambda x: pd.Timedelta(x, unit='D'))
    
    df_unique_sub_visits["VisitDate"] = date_time_obj
    df_unique_sub_visits["VisitDate"] = df_unique_sub_visits['VisitDate'] + temp 

    #pp.pprint(df_unique_sub_visits)
    #pp.pprint(df_demo)
    df_all_vars = df_all_vars.merge(df_unique_sub_visits, how="inner", on = ['SubjectNum', 'VisitDay'])
    # pp.pprint(df_all_vars)

    # Some times there seem to be multiple rows for the same event with different date. In such situations we are
    # arbitrarily deciding to use the last one that appears
    df_all_vars = df_all_vars.groupby(['SubjectNum', 'VisitDay']).last().reset_index()
    df_all_vars_sorted = df_all_vars.sort_values(by = ['SubjectNum', 'VisitDay'])

# Convert the wide format to long format to calculate the summary values such as change and rate of change
    df_all_vars_long = pd.melt(df_all_vars, id_vars=['SubjectNum', 'VisitDay', 'VisitNum', 'VisitCode', 'VisitDate'], var_name='Testname', value_name='Value')
    df_all_vars_long_sorted = df_all_vars_long.sort_values(by = ['SubjectNum', 'VisitDay'])
    df_all_vars_long_sorted = df_all_vars_long_sorted.dropna()
    print("All observations:")
    #pp.pprint(df_all_vars_long_sorted)

    # To calculate the difference and rate of change group by the patient and test
    df_grouped_tests = df_all_vars_long_sorted.groupby(['SubjectNum', 'Testname']).nth([0, -1]).reset_index()
    df_grouped_tests = df_grouped_tests.sort_values(by = ['SubjectNum', 'Testname','VisitDay'])
    df_grouped_tests = df_grouped_tests.dropna()

    #pp.pprint(df_grouped_tests)
    #exit()

    print("Generating summary information")
    df_groups_with_multiple = df_all_vars_long_sorted.groupby(['SubjectNum', 'Testname']).filter(lambda x: len(x) > 1)
    #pp.pprint(df_groups_with_multiple)
    # Filter out categorical variables from observations
    df_grouped_tests_summary = df_groups_with_multiple.groupby(['SubjectNum', 'Testname']).apply(calc_duration_change).reset_index()
    df_grouped_tests_summary = pd.melt(df_grouped_tests_summary.loc[:, ['SubjectNum', 'Testname', 'Change', 'ROC']], 
                                        id_vars=['SubjectNum', 'Testname'], var_name='Type', value_name="Value")
    df_grouped_tests_summary['Testname'] = df_grouped_tests_summary['Testname'] + "-" + df_grouped_tests_summary['Type']
    df_grouped_tests_summary = df_grouped_tests_summary.loc[:, ['SubjectNum', 'Testname', 'Value']] 
    print("Grouped test summary:")
    #pp.pprint(df_grouped_tests_summary)

    df_all_obs = df_all_vars_long_sorted

    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode']))
    filename = "UMDPD_obs.csv"
    df_all_vars_sorted.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_demo.sort_values(by = ['SubjectNum', 'Study']))
    filename = "UMDPD_demographics.csv"
    df_demo.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_demo_long)
    filename = "UMDPD_demographics_long.csv"
    df_demo_long.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_all_vars_long_sorted)
    filename = "UMDPD_obs_long.csv"
    df_all_obs.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_grouped_tests_summary)
    filename = "UMDPD_obs_summary.csv"
    df_grouped_tests_summary.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Before printing the subject visits calculate the age at visit
    df_demo_cols = df_demo.loc[:, ['SubjectNum', 'agefirstvisit', 'PDdurationatfirstvisit']].drop_duplicates()
    df_unique_sub_visits = df_unique_sub_visits.merge(df_demo_cols, how="inner", on = ['SubjectNum'])
    df_unique_sub_visits['Age At Visit'] = round((df_unique_sub_visits['agefirstvisit'] + (df_unique_sub_visits['VisitDay']/365)), 0 )
    df_unique_sub_visits['Disease Duration At Visit'] = round((df_unique_sub_visits['PDdurationatfirstvisit']) + (df_unique_sub_visits['VisitDay']/365))

    #pp.pprint(df_unique_sub_visits)

    # Print a table of visit information
    filename = "UMDPD_visit_info.csv"
    df_unique_sub_visits.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique tests in the data by combining the tests in the summary as well as observation
    # data frames
    unique_obs = df_all_obs.Testname.unique()
    unique_summary_obs = df_grouped_tests_summary.Testname.unique()
    unique_all_obs = np.concatenate([unique_obs, unique_summary_obs])
    #pp.pprint(unique_all_obs)
    # df_unique_obs = pd.DataFrame({"Observations": df_all_obs.Testname.unique()})
    df_unique_obs = pd.DataFrame({"Observations": unique_all_obs})
    #pp.pprint(df_unique_obs)
    filename = "UMDPD_unique_obs.csv"
    df_unique_obs.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique subject variables in the data
    df_unique_subject_vars = pd.DataFrame({"Observations": df_demo_long.SubjectVar.unique()})
    # pp.pprint(df_unique_subject_vars)
    filename = "UMDPD_unique_subject_vars.csv"
    df_unique_subject_vars.to_csv(os.path.join(args.output_dir, filename), index = False)


if __name__ == '__main__':
    main()
