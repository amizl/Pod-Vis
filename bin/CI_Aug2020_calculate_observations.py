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

CI_STUDY = "University of Iowa CI Aug2020"

ATTRIBUTE_METADATA = [
    {
        'abbrev': 'Study',
        'name': 'Study',
        'descr': "The original/uploaded dataset.",
    },
    {
        'abbrev': 'Sex',
        'name': 'Sex',
        'descr': "Binary gender, either 'Male' or 'Female'.",
    },
    {
        'abbrev': 'Marital Status',
        'name': 'Marital Status',
        'descr': "Either 'Married', 'Divorced', 'Widowed', or 'Unknown'.",
    },
    {
        'abbrev': 'Deceased',
        'name': 'Deceased',
        'descr': "Either 'Y' for yes or 'N' for no.",
    },
    {
        'abbrev': 'Ear1',
        'name': 'Implant 1 Ear',
        'descr': "Ear corresponding to first implantation: either 'L' for left, 'R' for right, or 'B' for both.",
    },
    {
        'abbrev': 'Ear2',
        'name': 'Implant 2 Ear',
        'descr': "Ear corresponding to second implantation: either 'L' for left, 'R' for right, or 'B' for both.",
    },
    {
        'abbrev': 'Ear3',
        'name': 'Implant 3 Ear',
        'descr': "Ear corresponding to third implantation: either 'L' for left, 'R' for right, or 'B' for both.",
    },
    {
        'abbrev': 'Type1',
        'name': 'Implant 1 Type',
        'descr': "Type of cochlear implant(s) used in first implantation.",
    },
    {
        'abbrev': 'Type2',
        'name': 'Implant 2 Type',
        'descr': "Type of cochlear implant(s) used in second implantation.",
    },
    {
        'abbrev': 'Type3',
        'name': 'Implant 3 Type',
        'descr': "Type of cochlear implant(s) used in third implantation.",
    },
    {
        'abbrev': 'UIHC1',
        'name': 'Implant 1 at UIHC',
        'descr': "Whether first implantation was performed at the University of Iowa Hearing Clinic: either 'Y' for yes or 'N' for no.",
    },
    {
        'abbrev': 'UIHC2',
        'name': 'Implant 2 at UIHC',
        'descr': "Whether second implantation was performed at the University of Iowa Hearing Clinic: either 'Y' for yes or 'N' for no.",
    },
    {
        'abbrev': 'UIHC3',
        'name': 'Implant 3 at UIHC',
        'descr': "Whether third implantation was performed at the University of Iowa Hearing Clinic: either 'Y' for yes or 'N' for no.",
    },
    {
        'abbrev': 'lAgeDeaf',
        'name': 'Age of Deafness Left Ear',
        'descr': "Age at which hearing was lost in the left ear.",
    },
    {
        'abbrev': 'rAgeDeaf',
        'name': 'Age of Deafness Right Ear',
        'descr': "Age at which hearing was lost in the right ear.",
    },
    {
        'abbrev': 'AgeAtImplantation',
        'name': 'Implant 1 Age',
        'descr': "Age at first implantation.",
    },
    {
        'abbrev': 'lPhysCauseLoss',
        'name': 'Cause of Left Sided Hearing Loss',
        'descr': "Cause of Left Sided Hearing Loss.",
    },
    {
        'abbrev': 'rPhysCauseLoss',
        'name': 'Cause of Right Sided Hearing Loss',
        'descr': "Cause of Right Sided Hearing Loss.",
    },
    {
        'abbrev': 'lAgeAidUse',
        'name': 'Age at Left Hearing Aid Use',
        'descr': 'Age at Left Hearing Aid Use',
    },
    {
        'abbrev': 'rAgeAidUse',
        'name': 'Age at Right Hearing Aid Use',
        'descr': 'Age at Right Hearing Aid Use',
    },
    {
        'abbrev': 'opdate1',
        'name': 'Date of Operation 1',
        'descr': 'Date of operation 1/first implantation.',
    },
    {
        'abbrev': 'opdate2',
        'name': 'Date of Operation 2',
        'descr': 'Date of operation 2/second implantation.',
    },
    {
        'abbrev': 'opdate3',
        'name': 'Date of Operation 3',
        'descr': 'Date of operation 3/third implantation.',
    },
    {
        'abbrev': 'condate1',
        'name': 'Date of Connection 1',
        'descr': 'Date of operation 1/first implantation device connection.',
    },
    {
        'abbrev': 'condate2',
        'name': 'Date of Connection 2',
        'descr': 'Date of operation 2/second implantation device connection.',
    },
    {
        'abbrev': 'condate3',
        'name': 'Date of Connection 3',
        'descr': 'Date of operation 3/third implantation device connection.',
    },
    {
        'abbrev': 'OpAge1',
        'name': 'Age at Operation 1',
        'descr': 'Age at operation 1/first implantation.',
    },
    {
        'abbrev': 'OpAge2',
        'name': 'Age at Operation 2',
        'descr': 'Age at operation 2/second implantation.',
    },
    {
        'abbrev': 'OpAge3',
        'name': 'Age at Operation 3',
        'descr': 'Age at operation 3/third implantation.',
    },
    {
        'abbrev': 'ConAge1',
        'name': 'Age at Connection 1',
        'descr': 'Age at operation 1/first implantation device connection.',
    },
    {
        'abbrev': 'ConAge2',
        'name': 'Age at Connection 2',
        'descr': 'Age at operation 2/second implantation device connection.',
    },
    {
        'abbrev': 'ConAge3',
        'name': 'Age at Connection 3',
        'descr': 'Age at operation 3/third implantation device connection.',
    },
]

TMT_DESCR = """The Trail Making Test is a neuropsychological test of visual attention and 
task switching. It can provide information about visual search speed, 
scanning, speed of processing, mental flexibility, as well as executive 
functioning. It was originally part of the Army Individual Test Battery 
(Armitage, 1946)."""

NEO_FF_DESCR = """The Revised NEO Personality Inventory (NEO PI-R) is a personality 
inventory that examines a person's Big Five personality traits (openness to experience, 
conscientiousness, extraversion, agreeableness, and neuroticism.)"""

BVMT_DESCR = """The Brief Visuospatial Memory Test is a commonly used, commercialized, 
assessment tool to measure visuospatial learning and memory abilities across research 
and clinical settings.
"""

HVLT_DESCR = """The Hopkins Verbal Learning Test is a test of verbal learning and memory. 
The test consists of three trials of free-recall of a 12-item, semantically categorized list, followed by yes/no recognition.
"""

WAIS_DESCR = """The Wechsler Adult Intelligence Scale (WAIS) is an IQ test designed to measure 
intelligence and cognitive ability in adults and older adolescents.[1] The original WAIS (Form I) 
was published in February 1955 by David Wechsler, as a revision of the Wechsler–Bellevue Intelligence 
Scale, released in 1939. It is currently in its fourth edition (WAIS-IV) released in 2008 by Pearson, 
and is the most widely used IQ test, for both adults and older adolescents, in the world. 
"""

WRAT_DESCR = """The Wide Range Achievement Test 4 (WRAT4) is an academic skills assessment which 
measures reading skills, math skills, spelling, and comprehension.
"""

SCALE_METADATA = [

    # Trail Making Test
    {
        'abbrev': 'TMT A SS',
        'name': 'Trail Making Test Part A SS',
        'descr': TMT_DESCR,
    },
    {
        'abbrev': 'TMT A Secs',
        'name': 'Trail Making Test Part A Seconds to Complete',
        'descr': TMT_DESCR,
    },
    {
        'abbrev': 'TMT A T-score',
        'name': 'Trail Making Test Part A T-score',
        'descr': TMT_DESCR,
    },
    {
        'abbrev': 'TMT B SS',
        'name': 'Trail Making Test Part B SS',
        'descr': TMT_DESCR,
    },
    {
        'abbrev': 'TMT B Secs',
        'name': 'Trail Making Test Part B Seconds to Complete',
        'descr': TMT_DESCR,
    },
    {
        'abbrev': 'TMT B T-score',
        'name': 'Trail Making Test Part B T-score',
        'descr': TMT_DESCR,
    },

    # Neo Five Factor Inventory Personality Test
    {
        'abbrev': 'AgreeRank',
        'name': ' Neo Five Factor Inventory Agreeableness Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'AgreeRaw',
        'name': ' Neo Five Factor Inventory Agreeableness Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'AgreeTScore',
        'name': ' Neo Five Factor Inventory Agreeableness T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ConsciRank',
        'name': ' Neo Five Factor Inventory Conscientiousness Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ConsciRaw',
        'name': ' Neo Five Factor Inventory Conscientiousness Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ConsciTScore',
        'name': ' Neo Five Factor Inventory Conscientiousness T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ExtroRank',
        'name': ' Neo Five Factor Inventory Extraversion Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ExtroRaw',
        'name': ' Neo Five Factor Inventory Extraversion Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ExtroTScore',
        'name': ' Neo Five Factor Inventory Extraversion T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'NeuRank',
        'name': ' Neo Five Factor Inventory Neuroticism Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'NeuRaw',
        'name': ' Neo Five Factor Inventory Neuroticism Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'NeuTScore',
        'name': ' Neo Five Factor Inventory Neuroticism T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'OpenRank',
        'name': ' Neo Five Factor Inventory Openness Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'OpenRaw',
        'name': ' Neo Five Factor Inventory Openness Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'OpenTScore',
        'name': ' Neo Five Factor Inventory Openness T Score',
        'descr': NEO_FF_DESCR,
    },

    # BVMT - Brief Visuospatial Memory Test
    {
        'abbrev': 'BVMT-DR Raw',
        'name': ' BVMT Delayed Recall Raw',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-DR T Score',
        'name': ' BVMT Delayed Recall T-Score',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-TR Raw',
        'name': ' BVMT Total Recall Raw',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-TR T Score',
        'name': ' BVMT Total Recall T-Score',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-RD Raw',
        'name': ' BVMT Recall Discrimination Raw',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-RD Percentile',
        'name': ' BVMT Recall Discrimination Percentile',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BAITotalRaw',
        'name': ' Beck Anxiety Inventory',
        'descr': """The Beck Anxiety Inventory (BAI), created by Aaron T. Beck and other colleagues, is a 21-question 
multiple-choice self-report inventory that is used for measuring the severity of anxiety in children and adults. The 
questions used in this measure ask about common symptoms of anxiety that the subject has had during the past week 
(including the day you take it) (such as numbness and tingling, sweating not due to heat, and fear of the worst 
happening). It is designed for individuals who are of 17 years of age or older and takes 5 to 10 minutes to complete. 
Several studies have found the Beck Anxiety Inventory to be an accurate measure of anxiety symptoms in children and adults.""",
    },
    {
        'abbrev': 'BDITotalRaw',
        'name': ' Beck Depression Inventory',
        'descr': """The Beck Depression Inventory (BDI, BDI-1A, BDI-II), created by Aaron T. Beck, is a 21-question 
multiple-choice self-report inventory, one of the most widely used psychometric tests for measuring the severity of 
depression.""",
    },
    # HVLT - Hopkins Verbal Learning Test
    {
        'abbrev': 'HVLT-DR Raw',
        'name': 'HVLT Delayed Recall Raw',
        'descr': HVLT_DESCR,
    },
    {
        'abbrev': 'HVLT-DR T Score',
        'name': 'HVLT Delayed Recall T-Score',
        'descr': HVLT_DESCR,
    },
    {
        'abbrev': 'HVLT-TR Raw',
        'name': 'HVLT Total Recall Raw',
        'descr': HVLT_DESCR,
    },
    {
        'abbrev': 'HVLT-TR T Score',
        'name': 'HVLT Total Recall T-Score',
        'descr': HVLT_DESCR,
    },
    {
        'abbrev': 'HVLT-RD Index Raw',
        'name': 'HVLT Recall Discrimination Index Raw',
        'descr': HVLT_DESCR,
    },
    {
        'abbrev': 'HVLT-RD Index T Score',
        'name': 'HVLT Recall Discrimination Index T Score',
        'descr': HVLT_DESCR,
    },
    {
        'abbrev': 'HVLT-R Raw',
        'name': 'HVLT Retention Raw',
        'descr': HVLT_DESCR,
    },
    {
        'abbrev': 'HVLT-R T Score',
        'name': 'HVLT Retention T Score',
        'descr': HVLT_DESCR,
    },
    # WAIS
    {
        'abbrev': 'WAIS SimRaw',
        'name': 'WAIS Similarities Raw',
        'descr': WAIS_DESCR,
    },
    {
        'abbrev': 'WAIS Sim SS',
        'name': 'WAIS Similarities Symbol Search',
        'descr': WAIS_DESCR,
    },
    {
        'abbrev': 'WAIS DigSp Raw',
        'name': 'WAIS Digit Span Raw',
        'descr': WAIS_DESCR,
    },
    {
        'abbrev': 'WAIS DigSp SS',
        'name': 'WAIS Digit Span Symbol Search',
        'descr': WAIS_DESCR,
    },
    {
        'abbrev': 'WAIS MatReas Raw',
        'name': 'WAIS Matrix Reasoning Raw',
        'descr': WAIS_DESCR,
    },
    {
        'abbrev': 'WAIS MatReas SS',
        'name': 'WAIS Matrix Reasoning Symbol Search',
        'descr': WAIS_DESCR,
    },
    # WRAT
    {
        'abbrev': 'WRAT SimRaw',
        'name': 'WRAT Similarities Raw',
        'descr': WRAT_DESCR,
    },
    {
        'abbrev': 'WRAT Sim SS',
        'name': 'WRAT Similarities Symbol Search',
        'descr': WRAT_DESCR,
    },
    # Visit
    {
        'abbrev': 'Visit',
        'name': 'Visit',
        'descr': 'Subject visit year.',
    },
    # VisitDate
    {
        'abbrev': 'VisitDate',
        'name': 'Visit Date',
        'descr': 'Subject visit date.',
    },
]

#Visit
#VisitDate

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

def process_demographics(input_dir):

    demographics_filename = 'demo.csv'

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(os.path.join(input_dir, demographics_filename))
    
    # Recode some of the variables such as gender, race
    df_demo['Study'] = CI_STUDY

    df_demo["maritalStatus"] = df_demo["maritalStatus"].map(assign_MaritalStatus)
    df_demo['gender'] = df_demo['gender'].map(assign_Gender)

#    df_demo['AgeAtImplantation'] = df_demo['AgeAtImplantation'].map(lambda x: round(x))
    
    # Process some of the dates to assume the first of the month allow date operations
    # and then convert the datetime string to date
    df_demo[["opdate1", "condate1", "opdate2", "condate2", "opdate3", "condate3"]] = df_demo[["opdate1", "condate1", "opdate2", "condate2", "opdate3", "condate3"]].apply(lambda x: pd.to_datetime(x,  errors='raise'))

    # Calculate some of the numeric properties such as age at enrollment, age at diagnosis
    df_demo['OpAge1'] = df_demo['AgeAtImplantation']
    df_demo['ConAge1'] = ((df_demo['condate1'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['OpAge2'] = ((df_demo['opdate2'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['ConAge2'] = ((df_demo['condate2'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['OpAge3'] = ((df_demo['opdate3'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
    df_demo['ConAge3'] = ((df_demo['condate3'] - df_demo['opdate1']).dt.days/365.25) + df_demo['AgeAtImplantation']
        
    df_demo = df_demo.rename(columns={"SID": "SubjectNum", 
                                      "gender": "Sex",
                                      "maritalStatus": "Marital Status",
                                      "ear1": "Ear1",
                                      "ear2": "Ear2",
                                      "ear3": "Ear3",
                                      "DeceasedYN": "Deceased"},
                             errors="raise")

    print("df_demo:")
    print(df_demo)

    return df_demo

# convert simple test_sess (e.g., "229R") to year value between approx -5 and 33
def test_sess_simple_to_year(ts):
    year = None
    m = re.match(r'^([\d\-\.]+)a?[LR]$', ts)
    if m:
        # by 2 years
#        year = int(float(m.group(1)) / 24.0)
        
        # by year
        year = int(float(m.group(1)) / 12.0)

        # by 6 month increments
#        year = int(float(m.group(1)) / 6.0)
#        year = year / 2.0
    else:
        sys.stderr.write("couldn't parse test_sess " + ts)
        sys.exit()
    return str(year)

# convert simple test_sess (e.g., "229R/61L") to year value between approx -5 and 33
def test_sess_to_year(ts):
    yr = None

    if ts == "0":
        return "Y0"

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
                            "testdate": "VisitDate"}, 
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession', 'YrsEdu'], axis=1)
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
                            "testdate": "VisitDate"},
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession', 'YrsEdu'], axis=1)

    print("BDI:")
    pp.pprint(df)
    return df

def assign_Tscore(which):
    def afn(row):
        if (row[which] == '<1'):
            row[which] = 1
        if (row[which] == '<20') or (row[which] == '<=20'):
            row[which] = 20
        return row[which]
    return afn

#def assign_BVMT_DelRecTscore(row):
#    if (row["DelRecTscore"] == '<1'):
#        row["DelRecTscore"] = 1
#    if (row["DelRecTscore"] == '<20'):
#        row["DelRecTscore"] = 20
#    return row["DelRecTscore"]

def process_BVMT(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)

    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)

    # replace "<20" with "20", "<1" with "1"
    df["DelRecTscore"] = df[["DelRecTscore"]].apply(assign_Tscore('DelRecTscore'), axis = 1)
    df["TotRecTscore"] = df[["TotRecTscore"]].apply(assign_Tscore('TotRecTscore'), axis = 1)
    
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "VisitDate",
                            "TotRecRaw": "BVMT-TR Raw",
                            "TotRecTscore": "BVMT-TR T Score",
                            "DelRecRaw": "BVMT-DR Raw",
                            "DelRecTscore": "BVMT-DR T Score",
                            'RecDiscrimIndexRaw': "BVMT-RD Raw",
                            "RecDiscrimIndex%ile": "BVMT-RD Percentile"},
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession', 'YrsEdu'], axis=1)

    print("BVMT:")
    pp.pprint(df)
    return df

def process_HVLT(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)

    # replace "<20" and "<=20" with 20
    df["DelRecTscore"] = df[["DelRecTscore"]].apply(assign_Tscore('DelRecTscore'), axis = 1)
       
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "VisitDate",
                            "TotRecRaw": "HVLT-TR Raw",
                            "TotRecTscore": "HVLT-TR T Score",
                            "DelRecRaw": "HVLT-DR Raw",
                            "DelRecTscore": "HVLT-DR T Score",
                            "RecDiscrim IndexRaw": "HVLT-RD Index Raw",
                            "RecDiscrim IndexTscore": "HVLT-RD Index T Score",
                            "RetRaw": "HVLT-R Raw",
                            "RetTscore": "HVLT-R T Score"},
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession', 'YrsEdu'], axis=1)

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
                            "testdate": "VisitDate",
                            "A SS": "TMT A SS",
                            "A T-score": "TMT A T-score",
                            "A Seconds to Complete": "TMT A Secs",
                            "B SS": "TMT B SS",
                            "B T-score": "TMT B T-score",
                            "B Seconds to Complete": "TMT B Secs",},
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession', 'YrsEdu'], axis=1)
    
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
                            "testdate": "VisitDate",
                            "SimRaw": "WAIS SimRaw",
                            "Sim SS": "WAIS Sim SS",
                            "DigSp Raw": "WAIS DigSp Raw",
                            "DigSp SS": "WAIS DigSp SS",
                            "MatReas Raw": "WAIS MatReas Raw",
                            "MatReas SS": "WAIS MatReas SS"},
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession', 'YrsEdu'], axis=1)
    
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
                            "testdate": "VisitDate",
                            "SimRaw": "WRAT SimRaw",
                            "Sim SS": "WRAT Sim SS"},
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession', 'YrsEdu'], axis=1)

    print("WRAT:")
    pp.pprint(df)
    return df

def assign_Neu(which):
    def afn(row):
        if (row[which] == '<2'):
            row[which] = 2
        if (row[which] == '<25'):
            row[which] = 25
        return row[which]
    return afn

def process_NEO_FFI(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)

    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Visit'] = df["test_sess"].apply(test_sess_to_year)

    df["NeuRaw"] = df[["NeuRaw"]].apply(assign_Neu('NeuRaw'), axis = 1)
    df["NeuTScore"] = df[["NeuTScore"]].apply(assign_Neu('NeuTScore'), axis = 1)
        
    # take only first measurement if more than one
    df = df.groupby(['SID', 'Visit']).first().reset_index()

    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "VisitDate",},
                            errors="raise")

    df = df.drop(['test_sess', 'AgeAtSession'], axis=1)

    print("NEO_FFI:")
    pp.pprint(df)
    return df

def generate_field_mapping(df_unique_subj_vars, df_unique_obs, demographics_file, observations_file):
    fmcols = ['Category','Scale','Database Entity','Ontology Label','Source File','Entry Type','FieldName','Testname','Type','Data Type','Flip Axis','Ordinal Sort']
    fmvals = []
    
    # process subject attributes
    for index, row in df_unique_subj_vars.iterrows():
        obs = row['SubjectVar']
        label = row['Label']
        stype = ''
        data_type = ''
        flip_axis=''
        ordinal_sort = ''

        if re.match(r'^.*Age.*$', obs):
            stype = 'Decimal'
            data_type = 'Continuous'
        elif re.match(r'^.*[Dd]ate.*$', obs):
            stype = 'Date'
            data_type = 'Continuous'
        elif re.match(r'^(Sex|Marital Status|[Ee]ar\d|UIHC\d|Deceased|Type\d|Cause of|Study|[lr]PhysCause)', obs):
            stype = 'Char'
            data_type = 'Categorical'
            
        if stype == '':
            sys.stderr.write("Type/datatype could not be determined for " + obs + "\n")
            sys.stderr.flush()
            sys.exit(1)

        nr = ['Demographics','','subject_ontology',label,demographics_file,'Property',obs,obs,stype,data_type,flip_axis,ordinal_sort]
        fmvals.append(nr)

        # subject_visit?
#        fmvals.append([SubjectVisit,,subject_visit,event_date,ppmi_visit_info.csv,Property,VisitDate,VisitDate,Date,Continuous,,])
#        SubjectVisit,,subject_visit,visit_event,ppmi_visit_info.csv,Property,VisitCode,VisitCode,Char,Ordinal,,"BL,PW,RS1,SC,ST,U01,V01,V02,V03,V04,V05,V06,V07,V08,V09,V10,V11,V12,V13,V14,V15,V16"
#        SubjectVisit,,subject_visit,visit_num,ppmi_visit_info.csv,Property,VisitNumber,VisitNumber,Integer,Ordinal,,

    # process observation variables
    for index, row in df_unique_obs.iterrows():
        obs = row['Testname']

        if re.match(r'^Visit.*$', obs):
            continue

        obs_info = {

            # Trails - Trail Making Test - neuropsychological test of visual attention and task switching
            'TMT A SS': { 'cat': 'Cognitive', 'descr': 'Trails Part A SS', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'TMT A Secs' : { 'cat': 'Cognitive', 'descr': 'Trails Part A Seconds to Complete', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'TMT A T-score': { 'cat': 'Cognitive', 'descr': 'Trails Part A T-score', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'TMT B SS': { 'cat': 'Cognitive', 'descr': 'Trails Part B SS', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'TMT B Secs' : { 'cat': 'Cognitive', 'descr': 'Trails Part B Seconds to Complete', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'TMT B T-score': { 'cat': 'Cognitive', 'descr': 'Trails Part B T-score', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # BVMT - Brief Visuospatial Memory Test
            
            "BVMT-TR Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT-TR T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT-DR Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT-DR T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT-RD Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT-RD Percentile" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },
            
            # HVLT - Hopkins Verbal Learning Test
            "HVLT-TR Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT-TR T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT-DR Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT-DR T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT-RD Index Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT-RD Index T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT-R Raw": { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT-R T Score": { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # BAI - Beck Anxiety Inventory
            "BAITotalRaw" : { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # BDI - Beck Depression Index
            "BDITotalRaw" : { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # WAIS - Processing Wechsler Adult Intelligence Scale IV
            "WAIS SimRaw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS Sim SS" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS DigSp Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS DigSp SS" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS MatReas Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS MatReas SS" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # WRAT - Wide Range Achievement Test IV
            "WRAT SimRaw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WRAT Sim SS" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
        }

        # Neo Five Factor Inventory Personality Test
        neo_ff_factors = [
            { 'short': 'Neu', 'long': 'Neuroticism' },
            { 'short': 'Extro', 'long': 'Extraversion' },
            { 'short': 'Open', 'long': 'Openness' },
            { 'short': 'Agree', 'long': 'Agreeableness' },
            { 'short': 'Consci', 'long': 'Conscientiousness' }
        ]

        for f in ['Neu', 'Extro', 'Open', 'Agree', 'Consci']:
            obs_info[f + 'Raw'] = { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }
            obs_info[f + 'Rank'] = { 'cat': 'Mental Health', 'descr': None, 'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' }
            obs_info[f + 'TScore'] = { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }

            
        if obs not in obs_info:
            sys.stderr.write("Type/datatype could not be determined for " + obs + "\n")
            sys.stderr.flush()
            sys.exit(1)
            
        i = obs_info[obs]
        if i['descr'] is None:
            i['descr'] = obs
        
        nr = [i['cat'],'','observation_ontology',i['descr'],observations_file,'Observation','Testname',obs,i['type'],i['data_type'],i['flip_axis'],i['ordinal_sort']]
        fmvals.append(nr)
        
    df = pd.DataFrame(data=fmvals, columns=fmcols)
    print("field mapping df = " + str(df))
    
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

    # DEBUG
    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_colwidth', -1)
    
    # If the output dir is not specified then use the input dir
    if args.output_dir is None:
        args.output_dir = args.input_dir

    # Process the demographic variables
    df_demo = process_demographics(args.input_dir)
    df_demo_long = pd.melt(df_demo, id_vars=['SubjectNum'], var_name ='SubjectVar', value_name ='Value')
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

    # all data frames
    dframes = [df_BAI, df_BDI, df_BVMT, df_HVLT, df_Trails, df_WAIS, df_WRAT, df_NEO_FFI]
#    dframes = [df_AzBio, df_CNC, df_BAI, df_BDI, df_BVMT, df_HVLT, df_Trails, df_WAIS, df_WRAT, df_NEO_FFI]
    vcols = ['SubjectNum', 'Visit', 'VisitDate']

    # build mapping from Visit -> VisitDate
    # - group by Visit and use first visit for the VisitDate
    df_visits = dframes[0].loc[:, vcols]
    print("df_visits:")
    print(df_visits)
    
    for tdf in dframes[1:]:
        df_vis = tdf.loc[:, vcols]
        df_visits = df_visits.append(df_vis)

    # add VisitNum, VisitCode
    df_visits = df_visits.sort_values(by = ['SubjectNum', 'VisitDate']).groupby(['SubjectNum', 'Visit']).first().reset_index()
    df_visits['VisitNum'] = df_visits.groupby(['SubjectNum']).cumcount()+1
    df_visits['VisitCode'] = df_visits['Visit']

    pd.set_option('display.max_colwidth', -1)
    print("df_visits with VisitNum:")
    print(df_visits)
    
    # merge DataFrames without VisitDate
    df_all_vars = dframes[0]
    df_all_vars = df_all_vars.drop(['VisitDate'], axis=1)

    for tdf in dframes[1:]:
        tdf = tdf.drop(['VisitDate'], axis=1)
        df_all_vars = df_all_vars.merge(tdf, how="outer", on = ['SubjectNum', 'Visit'])
    
    # merge to add VisitDate and VisitNum back
    df_all_vars = df_all_vars.merge(df_visits, how="outer", on = ['SubjectNum', 'Visit'])
    
    # Get the unique visits for all the subjects and calculate visit number
#    df_unique_sub_visits = df_all_vars.sort_values(['SubjectNum', 'VisitDate']).loc[:, ['SubjectNum', 'Visit', 'VisitDate']]

    # number visits - add VisitNum
#    df_unique_sub_visits['VisitNum'] = df_unique_sub_visits.groupby(['SubjectNum']).cumcount()+1
#    df_unique_sub_visits['VisitCode'] = df_unique_sub_visits['Visit']
    # TODO - add Birthdate, AgeAtVisit?

    # add VisitNum, VisitDate
#    df_all_vars = df_all_vars.merge(df_unique_sub_visits, how="inner", on = ['SubjectNum', 'Visit', 'VisitDate'])

    # Some times there seem to be multiple rows for the same event with different date. In such situations we are
    # arbitrarily deciding to use the last one that appears
#    df_all_vars = df_all_vars.groupby(['SubjectNum', 'VisitCode']).last().reset_index()
    df_all_vars_sorted = df_all_vars.sort_values(by = ['SubjectNum', 'Visit'])

    # Convert the wide format to long format to calculate the summary values such as change and rate of change
    df_all_vars_long = pd.melt(df_all_vars, id_vars=['SubjectNum', 'VisitCode', 'VisitNum'], var_name='Testname', value_name='Value')
    df_all_vars_long_sorted = df_all_vars_long.sort_values(by = ['SubjectNum', 'Testname', 'VisitNum'])
    df_all_vars_long_sorted = df_all_vars_long_sorted.dropna()
    # don't report Visit, VisitDate as tests:
    df_all_vars_long_sorted = df_all_vars_long_sorted[df_all_vars_long_sorted.Testname != 'Visit']
    df_all_vars_long_sorted = df_all_vars_long_sorted[df_all_vars_long_sorted.Testname != 'VisitDate']
    
    # Once the dataframes are created write the table to a CSV file
    # pp.pprint(df_pilot_bio.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
    files = []

    # project file
    filename = "UI_CI_Aug2020_projects.csv"
    fpath = os.path.join(args.output_dir, filename)
    with open(fpath, 'w') as fh:
        fh.write("project_name,project_description,primary_disease,study_name,longitudinal,study_description\n")
        fh.write("University of Iowa CI,University of Iowa CI patients,Hearing Loss," + CI_STUDY + ",1,University of Iowa CI Aug2020\n")
    files.append(["Project", filename])
    
    df_all_vars.sort_values(by = ['SubjectNum'])
    filename = "UI_CI_Aug2020_obs.csv"

    print("Writing " + filename)
    df_all_vars.to_csv(os.path.join(args.output_dir, filename), index = False)
    # pp.pprint(df_demo.sort_values(by = ['SubjectNum', 'Study']))
    demographics_filename = "UI_CI_Aug2020_demographics.csv"
    print("Writing " + demographics_filename)
    df_demo.to_csv(os.path.join(args.output_dir, demographics_filename), index = False)

    # pp.pprint(df_demo_long)
    filename = "UI_CI_Aug2020_demographics_long.csv"
    files.append(["Subject Info", filename])
    print("Writing " + filename)
    df_demo_long.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_all_vars_long_sorted)

    observations_filename = "UI_CI_Aug2020_obs_long.csv"
    files.append(["Observations", observations_filename])
    print("Writing " + filename)
    df_all_vars_long_sorted.to_csv(os.path.join(args.output_dir, observations_filename), index = False)

    # Before printing the subject visits calculate the age at visit
#    df_unique_sub_visits = df_unique_sub_visits.merge(df_demo.loc[:, ['SubjectNum', 'Birthdate']], how="inner", on = ['SubjectNum'])
#    df_unique_sub_visits['AgeAtVisit'] = df_unique_sub_visits["AgeAtNow"]
#    df_unique_sub_visits['AgeAtVisit'] = df_unique_sub_visits
    # pp.pprint(df_unique_sub_visits)
    
    # Print a table of visit information
    #
    # e.g., 
    # SubjectNum,VisitCode,VisitDate,VisitNum,Birthdate,AgeAtVisit
    # 3000,SC,2011-01-01,1,1941-12-01,69.1
    # 3000,BL,2011-02-01,2,1941-12-01,69.2
    filename = "UI_CI_Aug2020_visit_info.csv"
    files.append(["Visit", filename])
    print("Writing " + filename)
    df_visits.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique observation variables in the data
    unique_obs = df_all_vars_long.Testname.unique()
    df_unique_obs = pd.DataFrame({"Testname": unique_obs}).sort_values(by = ['Testname'])
    # add scale metadata
    df_unique_obs = add_scale_metadata(df_unique_obs)
    filename = "UI_CI_Aug2020_unique_obs.csv"
    files.append(["Observation Ontology", filename])
    print("Writing " + filename)
    df_unique_obs.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique subject variables in the data
    df_unique_subject_vars = pd.DataFrame({"SubjectVar": df_demo_long.SubjectVar.unique()})
    # add scale metadata
    df_unique_subject_vars = add_attribute_metadata(df_unique_subject_vars)
    # pp.pprint(df_unique_subject_vars)
    filename = "UI_CI_Aug2020_unique_subject_vars.csv"
    files.append(["Subject Ontology", filename])
    print("Writing " + filename)
    df_unique_subject_vars.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Field mapping table
    df_field_mapping = generate_field_mapping(df_unique_subject_vars, df_unique_obs, demographics_filename, observations_filename)
    filename = "UI_CI_Aug2020_field_mapping.csv"
    print("Writing " + filename)
    df_field_mapping.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Files file
    filename = "UI_CI_Aug2020_files.csv";
    fpath = os.path.join(args.output_dir, filename)
    with open(fpath, 'w') as fh:
        fh.write("Entity,File\n");
        fh.write("\n".join([",".join(f) for f in files]) + "\n")
    
if __name__ == '__main__':
    main()
