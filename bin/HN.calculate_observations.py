#!/usr/bin/env python3

import argparse
import re
import sys
import pandas as pd
import numpy as np
import pprint
import datetime as dt

ATTRIBUTE_METADATA = [
    {
        'abbrev': 'Study',
        'name': 'Study',
        'descr': "The original/uploaded dataset.",
    },
    {
        'abbrev': 'Race',
        'name': 'Race',
        'descr': "Subject race: either 'White', 'Black', or 'Other'.",
    },
    {
        'abbrev': 'Birthdate',
        'name': 'Birthdate',
        'descr': "Subject birthdate.",
    },
    {
        'abbrev': 'Sex',
        'name': 'Sex',
        'descr': "Binary gender, either 'Male' or 'Female'.",
    },
    {
        'abbrev': 'Ever smoker',
        'name': 'Ever smoker',
        'descr': "Whether the subject has ever smoked: either 'Smoker' or 'Nonsmoker'.",
    },
    {
        'abbrev': 'Ever drinker',
        'name': 'Ever drinker',
        'descr': "Whether the subject has ever consumed alcoholic beverages: either 'Drinker' or 'Nondrinker'.",
    },
    {
        'abbrev': 'Age At Enrollment',
        'name': 'Age At Enrollment',
        'descr': "Subject age at study enrollment.",
    },
    {
        'abbrev': 'Age At Diagnosis',
        'name': 'Age At Diagnosis',
        'descr': "Subject age at primary disease diagnosis.",
    },
    {
        'abbrev': 'Diagnosis Date',
        'name': 'Diagnosis Date',
        'descr': "Date of subject's primary disease diagnosis.",
    },
    {
        'abbrev': 'Enroll Date',
        'name': 'Enroll Date',
        'descr': "Date of subject's study enrollment.",
    },
    {
        'abbrev': 'Follow-up Date',
        'name': 'Date of Last Follow-Up',
        'descr': "Date of subject's most recent follow-up visit.",
    },
]

SCALE_METADATA = [
    {
        'abbrev': 'Occurrence #',
        'name': 'Occurrence number',
        'descr': "Occurrence number: either '1st primary', 'other primary', 'recurrence', or 'Unknown'.",
    },
    {
        'abbrev': 'Tumor Stage',
        'name': 'Tumor Stage at 1st occurrence',
        'descr': "Indicates tumor stage at first occurrence: either T1, T2, T3, T4a, T4b, or Unknown",
    },
    {
        'abbrev': 'Nodal Stage',
        'name': 'Nodal Stage at 1st occurrence',
        'descr': "Indicates nodal stage at first occurrence: either N0, N1, N2, N3, N4, or Unknown.",
    },
    {
        'abbrev': 'Metastasis',
        'name': 'Metastases at 1st visit',
        'descr': "Indicates whether metastases were present at first visit: either M0, M1, or Unknown.",
    },
    {
        'abbrev': 'Overall Stage',
        'name': 'Overall TNM stage at 1st occurrence',
        'descr': "Indicated overall TNM stage at first occurrence: either I, II, III, IVa, IVb, IVc, or Unknown.",
    },
    {
        'abbrev': 'Research lab p16',
        'name': 'Research lab p16',
        'descr': "Laboratory testing evidence of p16 status: either 'p16 negative', 'p16 positive', or 'p16 unknown'.",
    },
    {
        'abbrev': 'Clinical lab p16',
        'name': 'Clinical lab p16',
        'descr': "Clinical assessment of p16 status: either 'p16 negative', 'p16 positive', or 'p16 unknown'.",
    },
    {
        'abbrev': 'Research lab HPV',
        'name': 'Research lab HPV',
        'descr': "Laboratory testing evidence of HPV status: either 'HPV negative', 'HPV positive', or 'HPV unknown'.",
    },
    {
        'abbrev': 'First Failure Type',
        'name': 'First Failure Type',
        'descr': "Type of first failure/recurrence: either 'locoregional', 'distant', 'locoregional and distant', or 'no known failure'.",
    },
    {
        'abbrev': 'Second Failure Type',
        'name': 'Second Failure Type',
        'descr': "Type of second failure/recurrence: either 'locoregional', 'distant', 'locoregional and distant', or 'no known failure'.",
    },
    {
        'abbrev': 'Status',
        'name': 'Status',
        'descr': "Subject status: either 'Alive w/o disease', 'Alive w/ disease', 'Dead w/o disease', 'Dead w/ disease', 'Alive unk disease', 'Dead unk disease', or 'Unknown'.",
    },
    {
        'abbrev': 'Treatment Modality',
        'name': 'Treatment Modality',
        'descr': "Treatment used in the first documented occurrence: either 'CTX-RT', 'RT', 'CTX', 'Sx', 'Sx & RT', 'Sx & CTX-RT', 'Sx & CTX', or 'Unknown'.",
    },
    {
        'abbrev': 'Initial Chemotherapy Agent',
        'name': 'Initial Chemotherapy Agent',
        'descr': "First chemotherapy used in initial occurrence.",
    },
    {
        'abbrev': 'Second Line Chemotherapy Agent',
        'name': 'Second Line Chemotherapy Agent',
        'descr': 'Second line chemotherapeutic agent used in initial occurrence.',
    },
    {
        'abbrev': 'Radiation Dosage',
        'name': 'Radiation Dosage for initial occurrence',
        'descr': "The radiation dosage in grays received during treatment of the initial occurrence.",
    },
    {
        'abbrev': 'Tumor Site',
        'name': 'Tumor Site',
        'descr': "Location of tumor at presentation: either 'oral cavity', 'oropharynx', 'larynx', 'hypopharynx', 'multiple', or 'Unknown'.",
    },
    {
        'abbrev': 'First Failure Site',
        'name': 'First Failure Site',
        'descr': "Location of tumor at first failure/recurrence: either 'oral cavity', 'oropharynx', 'larynx', 'hypopharynx', 'multiple', or 'Unknown'.",
    },
    {
        'abbrev': 'First Failure Date',
        'name': 'First Failure Date',
        'descr': "Date of first failure/ recurrence.",
    },
    {
        'abbrev': 'First Failure Diagnosis Date',
        'name': 'First Failure Diagnosis Date',
        'descr': "Diagnosis date of the first failure/recurrence.",
    },
    {
        'abbrev': 'First Failure Initial Chemotherapy Agent',
        'name': 'First Failure Initial Chemotherapy Agent',
        'descr': "First chemotherapeutic agent used in the first failure/recurrence.",
    },
    {
        'abbrev': 'First Failure Second Line Chemotherapy Agent',
        'name': 'First Failure Second Line Chemotherapy Agent',
        'descr': "Second line chemotherapeutic agent used in first failure/recurrence.",
    },
    {
        'abbrev': 'First Failure Radiation Dosage',
        'name': 'First Failure Radiation Dosage',
        'descr': "The radiation dosage in grays received during treatment of the first failure/recurrence.",
    },
    {
        'abbrev': 'First Failure Treatment Modality',
        'name': 'First Failure Treatment Modality',
        'descr': "Treatment modality used in the first failure/recurrence: either 'CTX-RT', 'RT', 'CTX', 'Sx', 'Sx & RT', 'Sx & CTX-RT', 'Sx & CTX', or 'Unknown'.",
    },
    {
        'abbrev': 'Time to First Failure',
        'name': 'Time to First Failure',
        'descr': "Time in years between the end of the initial treatment and the first failure/recurrence.",
    },
    {
        'abbrev': 'Date of Death',
        'name': 'Date of Death',
        'descr': "Date of death.",
    },
    {
        'abbrev': 'Time to Death',
        'name': 'Time to Death',
        'descr': "Time in years between enrollment and death.",
    },
    {
        'abbrev': 'Age at Death',
        'name': 'Age at Death',
        'descr': "Age at death.",
    },
]

scale_file_map = {'demographics' : "HN_input_mod.csv",
                  'First Occurrence' : "HN_input_mod.csv",
                  'First Treatment': "HN_input_mod.csv",
                  'failure1': "HN_input_mod.csv",
                  'failure2': "HN_input_mod.csv",
                  'death': "HN_input_mod.csv"}

pp = pprint.PrettyPrinter(indent=4)

def assign_race(row):
    if (row['Race'] == 1):
        return "White"
    elif (row['Race'] == 2):
        return 'Black'
    elif (row['Race'] == 3):
        return 'Other'
    else:
        return "Unknown"

def assign_smoking(row):
    if (row["Ever smoker"] == 1):
        return "Smoker"
    elif (row["Ever smoker"] == 2):
        return "Nonsmoker"
    else:
        return "Unknown"

def assign_drinking(row):
    if (row["Ever drinker"] == 1):
        return "Drinker"
    elif (row["Ever drinker"] == 2):
        return "Nondrinker"
    else:
        return "Unknown"


def process_demographics(input_dir):

    data_filename = "HN_input_mod.csv"

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(input_dir + data_filename)

    # Subset the frame for the columns needed
    df_demo = df_demo.loc[:, ["lab code", "Reg: 1st contact Date", "Race", "Gender", "Birthdate", "Ever smoker", "Ever drinker", "Dx Date1", "Last f/u"]]

    #pp.pprint(df_demo)

    # Recode some of the variables such as gender, race
    df_demo['Study'] = "UMD Head and Neck Cancer Patients"
    df_demo['Race'] = df_demo[["Race"]].apply(assign_race, axis = 1)
    df_demo['Gender'] = df_demo["Gender"].map(lambda x: 'Female' if x == 2 else 'Male')
    df_demo['Ever smoker'] = df_demo[["Ever smoker"]].apply(assign_smoking, axis = 1)
    df_demo['Ever drinker'] = df_demo[["Ever drinker"]].apply(assign_drinking, axis = 1)

    # Process some of the dates to assume the first of the month allow date operations
    # and then convert the datetime string to date

    df_demo[['Reg: 1st contact Date', 'Birthdate', 'Dx Date1', "Last f/u"]] = df_demo[['Reg: 1st contact Date', 'Birthdate', 'Dx Date1', "Last f/u"]].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce'))

    # Calculate some of the numeric properties such as age at enrollemnt, age at diagnosis
    df_demo['Age At Enrollment'] = round((df_demo['Reg: 1st contact Date'] - df_demo['Birthdate']).dt.days/365.25, 1) 
    df_demo['Age At Diagnosis'] = round((df_demo['Dx Date1'] - df_demo['Birthdate']).dt.days/365.25, 1 )

    # Remove some of the unwanted columns from the demographic variables
    df_demo = df_demo.loc[:, ['lab code', 'Study', 'Race', 'Birthdate', 'Gender', 'Ever smoker', 'Ever drinker', 'Age At Enrollment', 
                              'Age At Diagnosis', 'Dx Date1', 'Reg: 1st contact Date', "Last f/u"]]
    df_demo = df_demo.rename(columns={"lab code": "SubjectNum",  
                            "Gender": "Sex",
                            "Reg: 1st contact Date": "Enroll Date",
                            "Dx Date1": "Diagnosis Date",
                            "Last f/u": "Follow-up Date"
                            }, 
                            errors="raise")
    pp.pprint(df_demo)
    return df_demo
    #exit()

def assign_occurrence1(row):
    if (row["Occur1#"] == 1):
        return "1st primary"
    elif (row["Occur1#"] == 2):
        return "other primary"
    elif (row["Occur1#"] == 3):
        return "recurrence"
    else:
        return "Unknown"

def assign_site1(row):
    if (row["Site1#"] == 1):
        return "oral cavity"
    elif (row["Site1#"] == 2):
        return "oropharynx"
    elif (row["Site1#"] == 3):
        return "larynx"
    elif (row["Site1#"] == 4):
        return "hypopharynx"
    elif (row["Site1#"] == 5):
        return "multiple"
    else:
        return "Unknown"

def assign_tumor1(row):
    if (row["T1#"] == 1):
        return "T1"
    elif (row["T1#"] == 2):
        return "T2"
    elif (row["T1#"] == 3):
        return "T3"
    elif (row["T1#"] == 4):
        return "T4a"
    elif (row["T1#"] == 5):
        return "T4b"
    else:
        return "Unknown"

def assign_node1(row):
    if (row["N1#"] == 0):
        return "N0"
    elif (row["N1#"] == 1):
        return "N1"
    elif (row["N1#"] == 2):
        return "N2"
    elif (row["N1#"] == 3):
        return "N3"
    elif (row["N1#"] == 4):
        return "N4"
    else:
        return "Unknown"

def assign_mets1(row):
    if (row["M1"] == 0):
        return "M0"
    elif (row["M1"] == 1):
        return "M1"
    else:
        return "Unknown"

def assign_stage1(row):
    if (row["Stage1#"] == 1):
        return "I"
    elif (row["Stage1#"] == 2):
        return "II"
    elif (row["Stage1#"] == 3):
        return "III"
    elif (row["Stage1#"] == 4):
        return "IVa"
    elif (row["Stage1#"] == 5):
        return "IVb"
    elif (row["Stage1#"] == 6):
        return "IVc"
    else:
        return "Unknown"

def assign_p16lab(row):
    if (row["p16lab"] == 0):
        return "p16 negative"
    elif (row["p16lab"] == 1):
        return "p16 positive"
    else:
        return "p16 unknown"

def assign_p16clin(row):
    if (row["p16clin"] == 0):
        return "p16 negative"
    elif (row["p16clin"] == 1):
        return "p16 positive"
    else:
        return "p16 unknown"

def assign_HPVbest(row):
    if (row["HPVbest"] == 0):
        return "HPV negative"
    elif (row["HPVbest"] == 1):
        return "HPV positive"
    else:
        return "HPV unknown"

def process_first_occurrence(filename):

    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)

    # "PATNO",CLINICAL_EVENT","TESTNAME","TESTVALUE"
    df = df.loc[:, ["lab code", "Occur1#", "Site1#", "T1#", "N1#", "M1", "Stage1#", "p16lab", "p16clin", "HPVbest"]]

    df['Occur1#'] = df[["Occur1#"]].apply(assign_occurrence1, axis = 1)
    df['Site1#'] = df[["Site1#"]].apply(assign_site1, axis = 1)
    df['T1#'] = df[["T1#"]].apply(assign_tumor1, axis = 1)
    df['N1#'] = df[["N1#"]].apply(assign_node1, axis = 1)
    df['M1'] = df[["M1"]].apply(assign_mets1, axis = 1)
    df['Stage1#'] = df[["Stage1#"]].apply(assign_stage1, axis = 1)
    df['p16lab'] = df[["p16lab"]].apply(assign_p16lab, axis =1)
    df['p16clin'] = df[["p16clin"]].apply(assign_p16clin, axis =1)
    df['HPVbest'] = df[["HPVbest"]].apply(assign_HPVbest, axis =1)

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['lab code']).first().reset_index()
    df = df.rename(columns={"lab code": "SubjectNum", 
                            "Occur1#": "Occurrence #", 
                            "Site1#": "Tumor Site", 
                            "T1#": "Tumor Stage",
                            "N1#": "Nodal Stage",
                            "M1": "Metastasis",
                            "Stage1#": "Overall Stage",
                            "p16lab": "Research lab p16",
                            "p16clin": "Clinical lab p16",
                            "HPVbest": "Research lab HPV"}, 
                            errors="raise")
    #pp.pprint(df)
    return df
    #exit()

def assign_treatmentmod1(row):
    if (row["TX mod1"] == 1):
        return "CTX-RT"
    elif (row["TX mod1"] == 2):
        return "RT"
    elif (row["TX mod1"] == 3):
        return "CTX"
    elif (row["TX mod1"] == 4):
        return "Sx"
    elif (row["TX mod1"] == 5):
        return "Sx & RT"
    elif (row["TX mod1"] == 6):
        return "Sx & CTX-RT"
    elif (row["TX mod1"] == 7):
        return "Sx & CTX"
    else:
        return "Unknown"

def process_first_treatment(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)

    # "PATNO",CLINICAL_EVENT","TESTNAME","TESTVALUE"
    df = df.loc[:, ["lab code", "TX mod1", "Total Primary Dose1", "ChemoAg1A",
                     "ChemoAg1B"]]
    
    df['TX mod1'] = df[["TX mod1"]].apply(assign_treatmentmod1, axis = 1)

    df = df.groupby(['lab code']).first().reset_index()
    df = df.rename(columns={"lab code": "SubjectNum", 
                            "TX mod1": "Treatment Modality",
                            "Total Primary Dose1": "Radiation Dosage",
                            "ChemoAg1A": "Initial Chemotherapy Agent",
                            "ChemoAg1B": "Second Line Chemotherapy Agent"},
                            errors = "raise")
    return df

def assign_failuretype1(row):
    if (row["Initial Failure Type1"] == 0):
        return "no known failure"
    elif (row["Initial Failure Type1"] == 1):
        return "locoregional"
    elif (row["Initial Failure Type1"] == 2):
        return "distant"
    elif (row["Initial Failure Type1"] == 3):
        return "locoregional and distant"
    else:
        return "no known failure"

def assign_site2(row):
    if (row["Site2#"] == 1):
        return "oral cavity"
    elif (row["Site2#"] == 2):
        return "oropharynx"
    elif (row["Site2#"] == 3):
        return "larynx"
    elif (row["Site2#"] == 4):
        return "hypopharynx"
    elif (row["Site2#"] == 5):
        return "multiple"

def assign_treatmentmod2(row):
    if (row["TX2"] == 1):
        return "CTX-RT"
    elif (row["TX2"] == 2):
        return "RT"
    elif (row["TX2"] == 3):
        return "CTX"
    elif (row["TX2"] == 4):
        return "Sx"
    elif (row["TX2"] == 5):
        return "Sx & RT"
    elif (row["TX2"] == 6):
        return "Sx & CTX-RT"
    elif (row["TX2"] == 7):
        return "Sx & CTX"

def process_failure1(filename):
    # Read the input as a pandas dataframe

    df = pd.read_csv(filename)

    df = df.loc[:, ["lab code", "Tx End1", "Failure date1", "Initial Failure Type1", "Site2#", "TX2",  "Total Primary Dose2", "ChemoAg2A", "ChemoAg2B"]]

    df["Site2#"] = df[["Site2#"]].apply(assign_site2, axis = 1)
    df['TX2'] = df[["TX2"]].apply(assign_treatmentmod2, axis = 1)
    df['Initial Failure Type1'] = df[["Initial Failure Type1"]].apply(assign_failuretype1, axis = 1)

    df[['Failure date1','Tx End1']] = df[['Failure date1','Tx End1']].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce'))

    df["Time to First Failure"] = round((df["Failure date1"] - df["Tx End1"]).dt.days/365.25, 1)


    df = df.loc[:, ["lab code", "Initial Failure Type1", "Failure?", "Site2#", "TX2", "Total Primary Dose2", "ChemoAg2A", "ChemoAg2B", "Time to First Failure"]]
    df = df.groupby(['lab code']).first().reset_index()
    df = df.rename(columns={"lab code": "SubjectNum", 
                            "Initial Failure Type1": "First Failure Type",
                            "Site2#": "First Failure Site",
                            "TX2": "First Failure Treatment Modality",
                            "Total Primary Dose2": "First Failure Radiation Dosage",  
                            "ChemoAg2A": "First Failure Initial Chemotherapy Agent",
                            "ChemoAg2B": "First Failure Second Line Chemotherapy Agent"}, 
                            errors="raise")
    return df

def assign_failuretype2(row):
    if (row["Failure Type2"] == 0):
        return "no known failure"
    elif (row["Failure Type2"] == 1):
        return "locoregional"
    elif (row["Failure Type2"] == 2):
        return "distant"
    elif (row["Failure Type2"] == 3):
        return "locoregional and distant"
    else:
        return "no known failure"

def process_failure2(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)

    df = df.loc[:, ["lab code", "Failure date2", "Tx End2", "Failure Type2"]]

    df['Failure Type2'] = df[["Failure Type2"]].apply(assign_failuretype2, axis = 1)

    df[['Failure date2','Tx End2']] = df[['Failure date2','Tx End2']].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce'))

    df["Time to second failure"] = round((df["Failure date2"] - df["Tx End2"]).dt.days/365.2, 1)

    df = df.loc[:, ["lab code", "Second failure?","Time to 2nd failure", "Failure Type2"]]
    df = df.groupby(['lab code']).first().reset_index()
    df = df.rename(columns={"lab code": "SubjectNum", 
                            "Failure Type2": "Second Failure Type"}, 
                            errors="raise")
    return df

def assign_statusnum(row):
    if (row["fullstatus#"] == 1):
        return "Alive w/o disease"
    elif (row["fullstatus#"] == 2):
        return "Alive w/ disease"
    elif (row["fullstatus#"] == 3):
        return "Dead w/o disease"
    elif (row["fullstatus#"] == 4):
        return "Dead w/ disease"
    elif (row["fullstatus#"] == 5):
        return "Alive unk disease"
    elif (row["fullstatus#"] == 6):
        return "Dead unk disease"
    else:
        return "Unknown"

def process_death(filename):
    df = pd.read_csv(filename)

    df = df.loc[:, ['lab code','Reg: 1st contact Date', 'Date of Death', 'Birthdate', 'fullstatus#']]

    df[["Reg: 1st contact Date", "Date of Death", "Birthdate"]] = df[["Reg: 1st contact Date", "Date of Death", "Birthdate"]].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y', errors='coerce'))

    df["Time to Death"] = round((df["Date of Death"] - df["Reg: 1st contact Date"]).dt.days/365.2, 1)

    df["Age at Death"] = round((df["Date of Death"] - df["Birthdate"]).dt.days/365.2, 1)

    df['fullstatus#'] = df[["fullstatus#"]].apply(assign_statusnum, axis = 1)

    df = df.loc[:, ["lab code", "Date of Death", "Time to Death", "Age at Death", "fullstatus#"]]
    df = df.groupby(['lab code']).first().reset_index()
    df = df.rename(columns={"lab code": "SubjectNum",
                            "fullstatus#": "Status"}, 
                            errors="raise")
    return df

def add_attribute_metadata(df):
    # index metadata by abbreviation
    md_index = {}
    for md in ATTRIBUTE_METADATA:
        abbrev = md['abbrev']
        if abbrev in md_index:
            sys.stderr.write("FATAL - duplicate entry in ATTRIBUTE_METADATA, abbreviation=" + abbrev)
            sys.stderr.flush()
            sys.exit(1)
        md_index[abbrev] = md

    def get_attribute_metadata(varname, which):
        if varname in md_index:
            return md_index[varname][which].replace('\n', '')
        else:
            sys.stderr.write("FATAL - couldn't find metadata entry for " + varname)
            sys.stderr.flush()
            sys.exit(1)

    df['Label'] = df['SubjectVar'].apply(lambda x: get_attribute_metadata(x, 'name'))
    df['Description'] = df['SubjectVar'].apply(lambda x: get_attribute_metadata(x, 'descr'))

    return df
        
def add_scale_metadata(df):
    # index metadata by abbreviation
    smd_index = {}
    for md in SCALE_METADATA:
        abbrev = md['abbrev']
        if abbrev in smd_index:
            sys.stderr.write("FATAL - duplicate entry in SCALE_METADATA, abbreviation=" + abbrev)
            sys.stderr.flush()
            sys.exit(1)
        smd_index[abbrev] = md

    def get_scale_metadata(testname, which):
        m = re.match(r'^(.*)(-(Change|ROC))$', testname)
        if m:
            base_testname = m.group(1)
            extension = m.group(2)
        else:
            base_testname = testname
            extension = ''
            
        if base_testname in smd_index:
            return smd_index[base_testname][which].replace('\n', '')
        else:
            sys.stderr.write("FATAL - couldn't find metadata entry for " + testname)
            sys.stderr.flush()
            sys.exit(1)

    df['Label'] = df['Testname'].apply(lambda x: get_scale_metadata(x, 'name'))
    df['Description'] = df['Testname'].apply(lambda x: get_scale_metadata(x, 'descr'))

    return df

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
        if (scale == 'First Occurrence'):
            print("Processing First Occurrence")
            df_first_occurrence = process_first_occurrence(args.input_dir + filename)
            # pp.pprint(df_semantic_fluency.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'First Treatment'):
            print("Processing First Treatment")
            df_first_treatment = process_first_treatment(args.input_dir + filename)
            # pp.pprint(df_benton_judgement.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'failure1'):
            print("Processing First Failure")
            df_failure1 = process_failure1(args.input_dir + filename)
            # pp.pprint(df_mds_updrs1_1.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'failure2'):
            print("Processing Second Failure")
            df_failure2 = process_failure2(args.input_dir + filename)
            # pp.pprint(df_mds_updrs1_2.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'death'):
            print("Processing Death")
            df_death = process_death(args.input_dir + filename)
        

    labels = ["SubjectNum", "Occurrence #", "Tumor Site", "Tumor Stage", "Nodal Stage", "Metastasis", "Overall Stage"]
    df_all_vars = df_first_occurrence
    df_all_vars = df_all_vars.merge(df_first_treatment, how="outer", on = ['SubjectNum'])
    df_all_vars = df_all_vars.merge(df_failure1, how="outer", on = ['SubjectNum'])
    df_all_vars = df_all_vars.merge(df_failure2, how="outer", on = ['SubjectNum'])
    df_all_vars = df_all_vars.merge(df_death, how="outer", on = ['SubjectNum'])
    df_all_vars["VisitNum"] = 1
    df_all_vars["VisitCode"] = 1

    df_all_vars = df_all_vars.groupby(['SubjectNum']).last().reset_index()
    df_all_vars_sorted = df_all_vars.sort_values(by = ['SubjectNum'])

    df_all_vars_long = pd.melt(df_all_vars, id_vars=['SubjectNum','VisitNum', 'VisitCode'], var_name='Testname', value_name='Value')
    df_all_vars_long_sorted = df_all_vars_long.sort_values(by = ['SubjectNum'])
    df_all_vars_long_sorted = df_all_vars_long_sorted.dropna()

    df_all_obs = df_all_vars_long_sorted

    print("All observations:")
    pp.pprint(df_all_vars)

    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
    filename = "HN_obs.csv"
    df_all_vars_sorted.to_csv(args.output_dir + filename, index = False)

    # pp.pprint(df_demo.sort_values(by = ['SubjectNum', 'Study']))
    filename = "HN_demographics.csv"
    df_demo.to_csv(args.output_dir + filename, index = False)

    # pp.pprint(df_demo_long)
    filename = "HN_demographics_long.csv"
    df_demo_long.to_csv(args.output_dir + filename, index = False)

    # pp.pprint(df_all_vars_long_sorted)
    filename = "HN_obs_long.csv"
    df_all_obs.to_csv(args.output_dir + filename, index = False)

    df_unique_sub_visits = df_all_vars.sort_values(['SubjectNum']).groupby(['SubjectNum']).last().reset_index().loc[:, ["SubjectNum"]]
    df_unique_sub_visits = df_unique_sub_visits.merge(df_demo.loc[:, ['SubjectNum', 'Enroll Date']], how="inner", on = ['SubjectNum'])
    df_unique_sub_visits = df_unique_sub_visits.sort_values(['SubjectNum'])
    pp.pprint(df_unique_sub_visits)
    df_unique_sub_visits['VisitNum'] = df_unique_sub_visits.groupby(['SubjectNum']).cumcount()+1
    df_unique_sub_visits['VisitCode'] = df_unique_sub_visits['VisitNum']

    df_unique_sub_visits["VisitDate"] = df_unique_sub_visits["Enroll Date"]

    df_unique_sub_visits = df_unique_sub_visits.merge(df_demo.loc[:, ['SubjectNum', 'Age At Enrollment', 'Age At Diagnosis']], how="inner", on = ['SubjectNum'])
    df_unique_sub_visits['Age At Visit'] = df_unique_sub_visits["Age At Enrollment"]
    df_unique_sub_visits['Disease Duration At Visit'] = round((df_unique_sub_visits['Age At Enrollment']) - (df_unique_sub_visits['Age At Diagnosis']))

    filename = "HN_visit_info.csv"
    df_unique_sub_visits.to_csv(args.output_dir + filename, index = False)

    unique_obs = df_all_obs.Testname.unique()
    unique_all_obs = np.concatenate([unique_obs])
    pp.pprint(unique_all_obs)
    df_unique_obs = pd.DataFrame({"Testname": unique_all_obs})
    # add scale metadata
    df_unique_obs = add_scale_metadata(df_unique_obs)
    pp.pprint(df_unique_obs)
    filename = "HN_unique_obs.csv"
    df_unique_obs.to_csv(args.output_dir + filename, index = False)

    # Print a table of unique subject variables in the data
    df_unique_subject_vars = pd.DataFrame({"SubjectVar": df_demo_long.SubjectVar.unique()})
    # add scale metadata
    df_unique_subject_vars = add_attribute_metadata(df_unique_subject_vars)

    # pp.pprint(df_unique_subject_vars)
    filename = "HN_unique_subject_vars.csv"
    df_unique_subject_vars.to_csv(args.output_dir + filename, index = False)

if __name__ == '__main__':
    main()
