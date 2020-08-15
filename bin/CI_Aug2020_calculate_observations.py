#!/usr/bin/env python3

"""
This script is used to parse the CI data and extract the unique observation names,
and observations and generate the subject and observation ontology list, subject attributes,
visit observations, and subject summary files from the file. If there are any transformations
that need to be performed on the data, they are performed here. For instance the calculation
of UPDRS Totals, Semantic Fluency Totals, etc. 

"""

import argparse
import re
import os
import sys
import pandas as pd
import numpy as np
import pprint
import datetime as dt

scale_file_map = {'CNC': "CNC.csv",
                   'edu': "edu.csv",
                   'AzBio' : "AzBio.csv",
                   'BAI' : "BAI.csv",
                   'BDI' : "BDI.csv",
                   'BVMT' : "BVMT.csv",
                   'HVLT' : "HVLT.csv",
                   'NEO_FFI': "NEO-FFI.csv",
                   'Trails': "Trails.csv",
                   'WAIS': "WAIS.csv",
                   'WRAT': 'WRAT.csv'
                   }
pp = pprint.PrettyPrinter(indent=4)

# Method to calculate the change and rate of change for each group passed as a dataframe
def calc_duration_change(group):
    sorted_group = group.sort_values(by = ['VisitDate'])
    # pp.pprint(sorted_group)
    min_index = 0
    max_index = group.shape[0] - 1
    # print(sorted_group.iloc[max_index, 1], sorted_group.iloc[min_index, 1])
    duration = round((sorted_group.iloc[max_index, 1] - sorted_group.iloc[min_index, 1]).days/365.25, 2)
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
    # pp.pprint(ds)
    return ds
    
def process_demographics(input_dir):

    demographics_filename = 'demo.csv'

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(os.path.join(input_dir, demographics_filename))
    
    # Recode some of the variables such as gender, race
    df_demo['Study'] = "University of Iowa CI Patients"

    df_demo["maritalStatus"] = df_demo["maritalStatus"].map(assign_MaritalStatus)
    df_demo['gender'] = df_demo['gender'].map(assign_Gender)

#    df_demo['AgeAtImplantation'] = df_demo['AgeAtImplantation'].map(lambda x: round(x))
    
    # Process some of the dates to assume the first of the month allow date operations
    # and then convert the datetime string to date
    df_demo[["opdate1", "condate1", "opdate2", "condate2", "opdate3", "condate3"]] = df_demo[["opdate1", "condate1", "opdate2", "condate2", "opdate3", "condate3"]].apply(lambda x: pd.to_datetime(x,  errors='raise'))

    # Calculate some of the numeric properties such as age at enrollment, age at diagnosis
    df_demo['Age At Connection 1'] = ((df_demo['condate1'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['Age At Operation 2'] = ((df_demo['opdate2'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['Age At Connection 2'] = ((df_demo['condate2'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['Age At Operation 3'] = ((df_demo['opdate3'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['Age At Connection 3'] = ((df_demo['condate3'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']

    df_demo = df_demo.rename(columns={"SID": "SubjectNum", 
                                      "AgeAtImplantation": "Age At Operation 1", 
                                      "gender": "Sex",
                                      "maritalStatus": "Marital Status",
                                      "opdate1": "Date of Operation 1",
                                      "condate1": "Date of Connection 1",
                                      "opdate2": "Date of Operation 2",
                                      "condate2": "Date of Connection 2",
                                      "opdate3": "Date of Operation 3",
                                      "condate3": "Date of Connection 3",
                                      "DeceasedYN": "Deceased",
                                      "lAgeDeaf": "Age of Deafness Left Ear",
                                      "rAgeDeaf": "Age of Deafness Right Ear",
                                      "rPhysCauseLoss": "Cause of Right Sided Hearing Loss",
                                      "lPhysCauseLoss": "Cause of Left Sided Hearing Loss",
                                      "lAgeAidUse": "Age at Left Hearing Aid Use",
                                      "rAgeAidUse": "Age at Right Hearing Aid Use"}, 
                            errors="raise")

    print("df_demo:")
    print(df_demo)

    return df_demo

# convert simple test_sess (e.g., "229R") to year value between approx -5 and 33
def test_sess_simple_to_year(ts):
    year = None
    m = re.match(r'^([\d\-\.]+)a?[LR]$', ts)
    if m:
        year = int(float(m.group(1)) / 12.0)
    else:
        sys.stderr.write("couldn't parse test_sess " + ts)
        sys.exit()
    return str(year)

# convert simple test_sess (e.g., "229R/61L") to year value between approx -5 and 33
def test_sess_to_year(ts):
    yr = None

    if ts == "0":
        return 0

    m = re.match(r'^(.*)\/(.*)$', ts)
    # handle "229R/61L" case
    if m:
        y1 = test_sess_simple_to_year(m.group(1))
        y2 = test_sess_simple_to_year(m.group(2))
        if y1 > y2:
            yr = y1
        else:
            yr = y2

    # handle "229R" case
    else:
        yr = test_sess_simple_to_year(ts)

    return "Y" + str(yr)
        
def process_YrsEdu(filename):
    df['YrsEdu'] = df.loc[:, ['SID','YrsEdu']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID','YrsEdu']]
    df = df.groupby(['SID']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "YrsEdu": "Years of Education"}, 
                            errors="raise")

def assign_MaritalStatus(st):
    map =  { 'M': 'Married', 'D': 'Divorced', 'W': 'Widowed' }
    if isinstance(st, str) and (st.upper() in map):
        return map[st.upper()]
    return 'Unknown'

def assign_Gender(g):
    map = { 'M': 'Male', 'F': 'Female', '': 'Unknown'}
    if isinstance(g, str) and (g.upper() in map):
        return map[g.upper()]
    return 'Unknown'

def process_CNC(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df = df.loc[:, ['SID','test_sess', 'AmplificationLeft', 'AmplificationRight', 'Condition', 'CncWord_Percent', 'CncPhon_Percent']]

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.rename(columns={"SID": "SubjectNum", 
                            "AmplificationLeft": "Type of Amplification Left Ear",
                            "AmplificationRight": "Type of Amplification Right Ear",
                            "CncWord_Percent": "CNC Word Percentage Correct",
                            "CncPhon_Percent": "CNC Phoneme Percentage Correct"}, 
                            errors="raise")
    pp.pprint(df)
    return df

def process_AZBio(filename, df_demo):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    print("AZBio before:")
    pp.pprint(df)

    df['Visit'] = df["test_sess"].apply(test_sess_to_year)

    df = df.rename(columns={"SID": "SubjectNum", 
                            "test_sess": "Test Session",
                            "AmplificationLeft": "Type of Amplification Left Ear",
                            "AmplificationRight": "Type of Amplification Right Ear",
                            "AzBioWord_Percent": "AZBio Percentage Correct"}, 
                            errors="raise")

    print(df)
    return df


def process_BAI(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)

    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()
    
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "BAITotalRaw": "Beck Anxiety Inventory"}, 
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession', 'YrsEdu'], axis=1)
    
    print("BAI:")
    pp.pprint(df)
    return df

def process_BDI(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)

    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)

    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "BDITotalRaw": "Beck Depression Index"}, 
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession', 'YrsEdu'], axis=1)

    print("BDI:")
    pp.pprint(df)
    return df

def process_BVMT(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)

    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)
    
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotRecRaw": "Total Recall Raw",
                            "TotRecTscore": "Total Recall T Score",
                            "DelRecRaw": "Delayed Recall Raw",
                            "DelRecTscore": "Delayed Recall T Score",
                            'RecDiscrimIndexRaw': 'Recall Discrimination Raw',
                            "RecDiscrimIndex%ile": "Recall Discrimination Percentile"},
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession', 'YrsEdu'], axis=1)

    print("BVMT:")
    pp.pprint(df)
    return df

def process_HVLT(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)
    
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotRecRaw": "Total Recall Raw",
                            "TotRecTscore": "Total Recall T Score",
                            "DelRecRaw": "Delayed Recall Raw",
                            "DelRecTscore": "Delayed Recall T Score",
                            "RecDiscrim IndexRaw": "Recall Discrimination Index Raw",
                            "RecDiscrim IndexTscore": "Recall Discrimination Index T Score",
                            "RetRaw": "Retention Raw",
                            "RetTscore": "Retention T Score"},
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession', 'YrsEdu'], axis=1)

    print("HVLT:")
    pp.pprint(df)
    return df

def process_Trails(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)
    
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date"}, 
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession', 'YrsEdu'], axis=1)
    
    print("Trails:")
    pp.pprint(df)
    return df

def process_WAIS(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)

    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)
    
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "SimRaw": "WAIS Similarities Raw",
                            "Sim SS": "WAIS Similarities Symbol Search",
                            "DigSp Raw": "WAIS Digit Span Raw",
                            "DigSp SS": "WAIS Digit Span Symbol Search",
                            "MatReas Raw": "WAIS Matrix Reasoning Raw",
                            "MatReas SS": "WAIS Matrix Reasoning Symbol Search"},
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession', 'YrsEdu'], axis=1)
    
    print("WAIS:")
    pp.pprint(df)
    return df

def process_WRAT(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)

    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)
    
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "SimRaw": "WRAT Similarities Raw",
                            "Sim SS": "WRAT Similarities Symbol Search"}, 
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession', 'YrsEdu'], axis=1)

    print("WRAT:")
    pp.pprint(df)
    return df

def process_NEO_FFI(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)

    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)
    
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "NeuRaw": "Neuroticism Raw Score",
                            "NeuRank": "Neuroticism Rank",
                            "NeuTScore": "Neuroticism T Score",
                            "ExtroRaw": "Extraversion Raw Score",
                            "ExtroRank": "Extraversion Rank",
                            "ExtroTScore": "Extraversion T Score",
                            "OpenRaw": "Openness Raw Score",
                            "OpenRank": "Openness Rank",
                            "OpenTScore": "Openness T Score",
                            "AgreeRaw": "Agreeableness Raw Score",
                            "AgreeRank": "Agreeableness Rank",
                            "AgreeTScore": "Agreeableness T Score",
                            "ConsciRaw": "Conscientiousness Raw Score",
                            "ConsciRank": "Conscientiousness Rank",
                            "ConsciTScore": "Conscientiousness T Score"}, 
                            errors="raise")

    df = df.drop(['test_sess', 'Visit Date', 'AgeAtSession'], axis=1)

    print("NEO_FFI:")
    pp.pprint(df)
    return df

def main():
    # Parse the arguments
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='Path to an input directory from where to get files' )
    parser.add_argument('-o', '--output_dir', type=str, required=False, help='Path to directory where the output files that will be generated' )
    args = parser.parse_args()

    # DEBUG
#    pd.set_option('display.max_rows', -1)
    pd.set_option('display.max_colwidth', -1)
    
    # If the output dir is not specified then use the input dir
    if args.output_dir is None:
        args.output_dir = args.input_dir

    # Process the demographic variables
    df_demo = process_demographics(args.input_dir)
    df_test = df_demo
    df_demo_long = pd.melt(df_test, id_vars=['SubjectNum'], var_name ='SubjectVar', value_name ='Value')
    df_demo_long = df_demo_long.dropna()

    # Cycle through the scales and calculate the totals or any other transformations that need to be made
    for scale, filename in scale_file_map.items():
        if (scale == 'CNC'):
            print("Processing Consonants Nucleus Consonants Test")
#            df_CNC = process_CNC(os.path.join(args.input_dir, filename))
        elif (scale == 'AzBio'):
            print("Processing AzBio Sentence Test")
#            df_AzBio = process_AZBio(os.path.join(args.input_dir, filename), df_demo)
        elif (scale == 'BAI'):
            print("Processing Beck Anxiety Inventory")
            df_BAI = process_BAI(os.path.join(args.input_dir, filename))
        elif (scale == 'BDI'):
            print("Processing Beck Depression Index")
            df_BDI = process_BDI(os.path.join(args.input_dir, filename))
        elif (scale == 'BVMT'):
            print("Processing Brief Visuospatial Memory Test")
            df_BVMT = process_BVMT(os.path.join(args.input_dir, filename))
        elif (scale == 'HVLT'):
            print("Processing Hopkins Verbal Learning Test")
            df_HVLT = process_HVLT(os.path.join(args.input_dir, filename))
        elif (scale == 'Trails'):
            print("Processing Trails")
            df_Trails = process_Trails(os.path.join(args.input_dir, filename))
        elif (scale == 'WAIS'):
            print("Processing Wechsler Adult Intelligence Scale IV")
            df_WAIS =  process_WAIS(os.path.join(args.input_dir, filename))
        elif (scale == 'WRAT'):
            print("Processing Wide Range Achievement Test IV")
            df_WRAT =  process_WRAT(os.path.join(args.input_dir, filename))
        elif (scale == 'NEO_FFI'):
            print("Processing Neo Five Factor Inventory Personality Test")
            df_NEO_FFI =  process_NEO_FFI(os.path.join(args.input_dir, filename))

    df_all_vars = df_BAI

#    df_all_vars = df_all_vars.merge(df_AzBio, how="outer", on = ['SubjectNum', 'VisitDate'])

#    df_all_vars = df_all_vars.merge(df_BAI, how="outer", on = ['SubjectNum', 'test_sess'])

    df_all_vars = df_all_vars.merge(df_BDI, how="outer", on = ['SubjectNum', 'Visit'])

    df_all_vars = df_all_vars.merge(df_BVMT, how="outer", on = ['SubjectNum', 'Visit'])

    df_all_vars = df_all_vars.merge(df_HVLT, how="outer", on = ['SubjectNum', 'Visit'])

    df_all_vars = df_all_vars.merge(df_Trails, how="outer", on = ['SubjectNum', 'Visit'])

    df_all_vars = df_all_vars.merge(df_WAIS, how="outer", on = ['SubjectNum', 'Visit'])

    df_all_vars = df_all_vars.merge(df_WRAT, how="outer", on = ['SubjectNum', 'Visit'])

    df_all_vars = df_all_vars.merge(df_NEO_FFI, how="outer", on = ['SubjectNum', 'Visit'])

    print("df_all_vars:")
    print(df_all_vars)

    # Get the unique visits for all the subjects and calculate visit number
#    df_unique_sub_visits = df_all_vars.sort_values(['SubjectNum', 'VisitDate']).groupby(['SubjectNum']).last().reset_index().loc[:, ["SubjectNum", "VisitDate"]]
#    df_unique_sub_visits = df_unique_sub_visits.sort_values(['SubjectNum', 'VisitDate'])
#    df_unique_sub_visits['VisitNum'] = df_unique_sub_visits.groupby(['SubjectNum']).cumcount()+1
#    df_unique_sub_visits['VisitCode'] = df_unique_sub_visits['VisitNum']

#    df_all_vars = df_all_vars.merge(df_unique_sub_visits, how="inner", on = ['SubjectNum', 'VisitDate'])
    # pp.pprint(df_all_vars)

    # Some times there seem to be multiple rows for the same event with different date. In such situations we are
    # arbitrarily deciding to use the last one that appears
#    df_all_vars = df_all_vars.groupby(['SubjectNum', 'VisitCode']).last().reset_index()
#    df_all_vars_sorted = df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate'])

    # Convert the wide format to long format to calculate the summary values such as change and rate of change
#    df_all_vars_long = pd.melt(df_all_vars, id_vars=['SubjectNum', 'VisitCode', 'VisitDate', 'VisitNum'], var_name='Testname', value_name='Value')
#    df_all_vars_long_sorted = df_all_vars_long.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate'])
#    df_all_vars_long_sorted = df_all_vars_long_sorted.dropna()
#    print("All observations:")
#    pp.pprint(df_all_vars_long_sorted)

    # To calculate the difference and rate of change group by the patient and test and sort by VisitDate
#    df_grouped_tests = df_all_vars_long_sorted.groupby(['SubjectNum', 'Testname']).nth([0, -1]).reset_index()
#    df_grouped_tests = df_grouped_tests.sort_values(by = ['SubjectNum', 'Testname', 'VisitDate'])
#    df_grouped_tests = df_grouped_tests.dropna()
    # pp.pprint(df_grouped_tests)

#    print("Generating summary information")
#    df_groups_with_multiple = df_all_vars_long_sorted.groupby(['SubjectNum', 'Testname']).filter(lambda x: len(x) > 1)
#    pp.pprint(df_groups_with_multiple)
    # Filter out categorical variables from observations
#    cat_vars_list = ["ESS_State", "REM_RBD_State", "GDS"]
#    df_groups_with_multiple = df_groups_with_multiple[~df_groups_with_multiple.Testname.isin(cat_vars_list)]
#    df_grouped_tests_summary = df_groups_with_multiple.groupby(['SubjectNum', 'Testname']).apply(calc_duration_change).reset_index()
#    df_grouped_tests_summary = pd.melt(df_grouped_tests_summary.loc[:, ['SubjectNum', 'Testname', 'Change', 'ROC']], 
#                                        id_vars=['SubjectNum', 'Testname'], var_name='Type', value_name="Value")
#    df_grouped_tests_summary['Testname'] = df_grouped_tests_summary['Testname'] + "-" + df_grouped_tests_summary['Type']
#    df_grouped_tests_summary = df_grouped_tests_summary.loc[:, ['SubjectNum', 'Testname', 'Value']] 
#    print("Grouped test summary:")
#    pp.pprint(df_grouped_tests_summary)

#    print("Merged observations:")
#    pp.pprint(df_all_obs)

    # Once the dataframes are created write the table to a CSV file
    # pp.pprint(df_pilot_bio.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))

    df_all_vars.sort_values(by = ['SubjectNum'])
    filename = "UI_CI_obs.csv"
    print("Writing " + filename)
    df_all_vars.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_demo.sort_values(by = ['SubjectNum', 'Study']))
    filename = "UI_CI_demographics.csv"
    print("Writing " + filename)
    df_demo.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_demo_long)
    filename = "UI_CI_demographics_long.csv"
    print("Writing " + filename)
    df_demo_long.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_all_vars_long_sorted)
#    filename = "UI_CI_obs_long.csv"
#    df_all_obs.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_grouped_tests_summary)
#    filename = "UI_CI_obs_summary.csv"
#    df_grouped_tests_summary.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Before printing the subject visits calculate the age at visit
#    df_unique_sub_visits = df_unique_sub_visits.merge(df_demo.loc[:, ['SubjectNum', 'Birthdate']], how="inner", on = ['SubjectNum'])
#    df_unique_sub_visits['AgeAtVisit'] = df_unique_sub_visits["AgeAtNow"]
#    df_unique_sub_visits['AgeAtVisit'] = df_unique_sub_visits
    # pp.pprint(df_unique_sub_visits)
    
    # Print a table of visit information
#    filename = "UI_CI_visit_info.csv"
#    df_unique_sub_visits.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique tests in the data by combining the tests in the summary as well as observation
    # data frames
#    unique_obs = df_all_obs.Testname.unique()
#    unique_summary_obs = df_grouped_tests_summary.Testname.unique()
#    unique_all_obs = np.concatenate([unique_obs, unique_summary_obs])
#    pp.pprint(unique_all_obs)
    # df_unique_obs = pd.DataFrame({"Observations": df_all_obs.Testname.unique()})
#    df_unique_obs = pd.DataFrame({"Observations": unique_all_obs})
#    pp.pprint(df_unique_obs)
#    filename = "UI_CI_unique_obs.csv"
#    df_unique_obs.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique subject variables in the data
    df_unique_subject_vars = pd.DataFrame({"Observations": df_demo_long.SubjectVar.unique()})
    # pp.pprint(df_unique_subject_vars)
    filename = "UI_CI_unique_subject_vars.csv"
    print("Writing " + filename)
    df_unique_subject_vars.to_csv(os.path.join(args.output_dir, filename), index = False)

if __name__ == '__main__':
    main()
