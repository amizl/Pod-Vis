#!/usr/bin/env python3

"""
This script is used to parse the EMA data.

"""

import argparse
import dateutil
import re
import os
import sys
import pandas as pd
import numpy as np
import pprint
import datetime as dt

EMA_STUDY = "University of Iowa EMA Nov2020 v1"
OUTPUT_PREFIX = "EMA_Nov2020"

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

    # EMA
    {
        'abbrev': 'ACS1prec',
        'name': 'Speech Activity 1 prec',
        'descr': 'Speech Activity 1 prec',
    },
    {
        'abbrev': 'ACS2prec',
        'name': 'Speech Activity 2 prec',
        'descr': 'Speech Activity 2 prec',
    },
    {
        'abbrev': 'ACS3prec',
        'name': 'Speech Activity 3 prec',
        'descr': 'Speech Activity 3 prec',
    },
    {
        'abbrev': 'ACS4prec',
        'name': 'Speech Activity 4 prec',
        'descr': 'Speech Activity 4 prec',
    },
    {
        'abbrev': 'ACS5prec',
        'name': 'Speech Activity 5 prec',
        'descr': 'Speech Activity 5 prec',
    },
    
    # AZBio
    {
        'abbrev': 'AzBioWord_Percent',
        'name': 'AZBio percentage of words correct.',
        'descr': """The AzBio Sentence Test is a speech intelligibility test. The AzBio sentence corpus 
includes 1000 sentences recorded from two female and two male talkers. 165 sentences were selected from 
each talker and then assigned to 33 lists of 20 sentences, each having 5 sentences from each talker.
""",
    },
    {
        'abbrev': 'AzBioWord_Percent_Quiet',
        'name': 'AZBio percentage of words correct under quiet listening condition.',
        'descr': """The AzBio Sentence Test is a speech intelligibility test. The AzBio sentence corpus 
includes 1000 sentences recorded from two female and two male talkers. 165 sentences were selected from 
each talker and then assigned to 33 lists of 20 sentences, each having 5 sentences from each talker.
""",
    },
    {
        'abbrev': 'AzBioWord_Percent_NotQuiet',
        'name': 'AZBio percentage of words correct under non-quiet listening condition.',
        'descr': """The AzBio Sentence Test is a speech intelligibility test. The AzBio sentence corpus 
includes 1000 sentences recorded from two female and two male talkers. 165 sentences were selected from 
each talker and then assigned to 33 lists of 20 sentences, each having 5 sentences from each talker.
""",
    },

    # CNC
    {
        'abbrev': 'CncWord_Percent',
        'name': 'CNC percentage of words correct.',
        'descr': """CNC percentage of words correct.
""",
    },
    {
        'abbrev': 'CncPhon_Percent',
        'name': 'CNC percentage of phonemes correct.',
        'descr': """CNC percentage of phonemes correct.
""",
    },
    
    # CNC Best
    {
        'abbrev': 'CncBestWord_Percent',
        'name': 'CNC percentage of words correct for the highest-scoring CNC result.',
        'descr': """CNC percentage of words correct for the highest-scoring CNC result at a given visit/test.
""",
    },
    {
        'abbrev': 'CncBestPhon_Percent',
        'name': 'CNC percentage of phonemes correct for the highest-scoring CNC result.',
        'descr': """CNC percentage of phonemes correct for the highest-scoring CNC result at a given visit/test.
""",
    },
    {
        'abbrev': 'CncBest_Condition',
        'name': 'Condition for the highest-scoring CNC result.',
        'descr': """Listening condition for the highest-scoring CNC result at a given visit/test.',
""",
    },
    {
        'abbrev': 'CncBest_AmpLeft',
        'name': 'AmplificationLeft for the highest-scoring CNC result.',
        'descr': """AmplificationLeft for the highest-scoring CNC result at a given visit/test.',
""",
    },
    {
        'abbrev': 'CncBest_AmpRight',
        'name': 'AmplificationRight for the highest-scoring CNC result.',
        'descr': """AmplificationRight for the highest-scoring CNC result at a given visit/test.',
""",
    },

        # CNC Worst
    {
        'abbrev': 'CncWorstWord_Percent',
        'name': 'CNC percentage of words correct for the lowest-scoring CNC result.',
        'descr': """CNC percentage of words correct for the lowest-scoring CNC result at a given visit/test.
""",
    },
    {
        'abbrev': 'CncWorstPhon_Percent',
        'name': 'CNC percentage of phonemes correct for the lowest-scoring CNC result.',
        'descr': """CNC percentage of phonemes correct for the lowest-scoring CNC result at a given visit/test.
""",
    },
    {
        'abbrev': 'CncWorst_Condition',
        'name': 'Condition for the lowest-scoring CNC result.',
        'descr': """Listening condition for the lowest-scoring CNC result at a given visit/test.',
""",
    },
    {
        'abbrev': 'CncWorst_AmpLeft',
        'name': 'AmplificationLeft for the lowest-scoring CNC result.',
        'descr': """AmplificationLeft for the lowest-scoring CNC result at a given visit/test.',
""",
    },
    {
        'abbrev': 'CncWorst_AmpRight',
        'name': 'AmplificationRight for the lowest-scoring CNC result.',
        'descr': """AmplificationRight for the lowest-scoring CNC result at a given visit/test.',
""",
    },

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
        'name': 'Neo Five Factor Inventory Agreeableness Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'AgreeRaw',
        'name': 'Neo Five Factor Inventory Agreeableness Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'AgreeTScore',
        'name': 'Neo Five Factor Inventory Agreeableness T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ConsciRank',
        'name': 'Neo Five Factor Inventory Conscientiousness Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ConsciRaw',
        'name': 'Neo Five Factor Inventory Conscientiousness Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ConsciTScore',
        'name': 'Neo Five Factor Inventory Conscientiousness T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ExtroRank',
        'name': 'Neo Five Factor Inventory Extraversion Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ExtroRaw',
        'name': 'Neo Five Factor Inventory Extraversion Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'ExtroTScore',
        'name': 'Neo Five Factor Inventory Extraversion T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'NeuRank',
        'name': 'Neo Five Factor Inventory Neuroticism Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'NeuRaw',
        'name': 'Neo Five Factor Inventory Neuroticism Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'NeuTScore',
        'name': 'Neo Five Factor Inventory Neuroticism T Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'OpenRank',
        'name': 'Neo Five Factor Inventory Openness Rank',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'OpenRaw',
        'name': 'Neo Five Factor Inventory Openness Raw Score',
        'descr': NEO_FF_DESCR,
    },
    {
        'abbrev': 'OpenTScore',
        'name': 'Neo Five Factor Inventory Openness T Score',
        'descr': NEO_FF_DESCR,
    },

    # BVMT - Brief Visuospatial Memory Test
    {
        'abbrev': 'BVMT-DR Raw',
        'name': 'BVMT Delayed Recall Raw',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-DR T Score',
        'name': 'BVMT Delayed Recall T-Score',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-TR Raw',
        'name': 'BVMT Total Recall Raw',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-TR T Score',
        'name': 'BVMT Total Recall T-Score',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-RD Raw',
        'name': 'BVMT Recall Discrimination Raw',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BVMT-RD Percentile',
        'name': 'BVMT Recall Discrimination Percentile',
        'descr': BVMT_DESCR,
    },
    {
        'abbrev': 'BAITotalRaw',
        'name': 'Beck Anxiety Inventory',
        'descr': """The Beck Anxiety Inventory (BAI), created by Aaron T. Beck and other colleagues, is a 21-question 
multiple-choice self-report inventory that is used for measuring the severity of anxiety in children and adults. The 
questions used in this measure ask about common symptoms of anxiety that the subject has had during the past week 
(including the day you take it) (such as numbness and tingling, sweating not due to heat, and fear of the worst 
happening). It is designed for individuals who are of 17 years of age or older and takes 5 to 10 minutes to complete. 
Several studies have found the Beck Anxiety Inventory to be an accurate measure of anxiety symptoms in children and adults.""",
    },
    {
        'abbrev': 'BDITotalRaw',
        'name': 'Beck Depression Inventory',
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

pp = pprint.PrettyPrinter(indent=4)

def process_demographics(input_dir):

    demographics_filename = 'demo.csv'

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(os.path.join(input_dir, demographics_filename))
    
    # Recode some of the variables such as gender, race
    df_demo['Study'] = EMA_STUDY

    df_demo["maritalStatus"] = df_demo["maritalStatus"].map(assign_MaritalStatus)
    df_demo['gender'] = df_demo['gender'].map(assign_Gender)

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

#    print("df_demo:")
#    print(df_demo)

    return df_demo

def process_longitudinal_data(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)

    df['Visit'] = df['Session']
    df['VisitCode'] = df['Session']
    df = df.rename(columns={"ID": "SubjectNum",
                            "DelRecTscoreBVMT": "BVMT-DR T Score",
                            "TotRecTscoreBVMT": "BVMT-TR T Score",
                            "DelRecTscoreHVLT": "HVLT-DR T Score",
                            "TotRecTscoreHVLT": "HVLT-TR T Score",
                            "RecDiscrimIndexTscoreHVLT": "HVLT-RD Index T Score",
                            "RetTscoreHVLT": "HVLT-R T Score",
                            "DigSpSSWAIS": "WAIS DigSp SS",
                            "SimSSWAIS": "WAIS Sim SS",
                            "MatReasSSWAIS": "WAIS MatReas SS",
                            "SimSSWRAT": "WRAT Sim SS",
    },
                   errors="raise")

    df = df.drop(['Session'], axis=1)

#    print("df_long:")
#    print(df)
    
    return df

def azbio_quiet(row):
    pct = row['AzBioWord_Percent']
    cond = row['Condition']
#    print("checking cond=" + str(cond))
    if re.match(r'.*Quiet.*', str(cond)):
        return pct
    return None

def azbio_notquiet(row):
    pct = row['AzBioWord_Percent']
    cond = row['Condition']
#    amp_l = row['AmplficationLeft']
#    amp_r = row['AmplificationRight']
    if re.match(r'.*Quiet.*', str(cond)):
        return None
    return pct

def process_YrsEdu(filename):
    df['YrsEdu'] = df.loc[:, ['SID','YrsEdu']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID','YrsEdu']]
    df = df.groupby(['SID']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "YrsEdu": "Years of Education"}, 
                            errors="raise")

def assign_VisitNumber(g):
    map = { 'Pre': 1, '3 mo': 2, '6 mo': 3 }
    return map[g]

def assign_VisitDate(g):
    map = { 'Pre': 0, '3 mo': 3, '6 mo': 6 }
    months = map[g]
    base = dt.date(1900,1,1)
    return base + dateutil.relativedelta.relativedelta(months=int(months))

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
            # AzBio
            'AzBioWord_Percent': { 'cat': 'General Disease Severity', 'descr': 'AZBio percentage of words correct.',
                                         'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'AzBioWord_Percent_Quiet': { 'cat': 'General Disease Severity', 'descr': 'AZBio percentage of words correct under quiet listening condition.',
                                         'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'AzBioWord_Percent_NotQuiet': { 'cat': 'General Disease Severity', 'descr': 'AZBio percentage of words correct under non-quiet listening condition.',
                                            'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # CNC
            'CncWord_Percent': { 'cat': 'General Disease Severity', 'descr': 'CNC percentage of words correct.',
                                 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncPhon_Percent': { 'cat': 'General Disease Severity', 'descr': 'CNC percentage of phonemes correct.',
                                 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # CNC-Best
            'CncBestWord_Percent': { 'cat': 'General Disease Severity', 'descr': 'CNC percentage of words correct.',
                                     'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncBestPhon_Percent': { 'cat': 'General Disease Severity', 'descr': 'CNC percentage of phonemes correct.',
                                     'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncBest_Condition': { 'cat': 'General Disease Severity', 'descr': 'CNC best listening condition.',
                                   'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncBest_AmpLeft': { 'cat': 'General Disease Severity', 'descr': 'CNC best AmplificationLeft.',
                                 'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncBest_AmpRight': { 'cat': 'General Disease Severity', 'descr': 'CNC best AmplificationRight.',
                                  'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },

            # CNC-Worst
            'CncWorstWord_Percent': { 'cat': 'General Disease Severity', 'descr': 'CNC percentage of words correct.',
                                     'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncWorstPhon_Percent': { 'cat': 'General Disease Severity', 'descr': 'CNC percentage of phonemes correct.',
                                     'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncWorst_Condition': { 'cat': 'General Disease Severity', 'descr': 'CNC worst listening condition.',
                                   'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncWorst_AmpLeft': { 'cat': 'General Disease Severity', 'descr': 'CNC worst AmplificationLeft.',
                                 'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },
            'CncWorst_AmpRight': { 'cat': 'General Disease Severity', 'descr': 'CNC worst AmplificationRight.',
                                  'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },

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

        # EMA - handle all /.*avg/
        for p in ['VC', 'TF', 'NZ', 'SNR', 'SP', 'LE', 'LCL', 'SQ', 'ST', 'AR', 'DP', 'SI', 'AX', 'IM']:
            obs_info[p + 'avg'] = { 'cat': 'General Disease Severity', 'descr': p + " average", 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }
        
        # EMA - handle all /.*prec/

        # LC1-LC4
        for n in range(1,5):
            p = 'LC' + str(n) + 'prec'
            obs_info[p] = { 'cat': 'General Disease Severity', 'descr': p, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }
        
        # AL1
        obs_info['AL1prec'] = { 'cat': 'General Disease Severity', 'descr': 'AL1', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }
        
        # SN1-SN3
        for n in range(1,4):
            p = 'SN' + str(n) + 'prec'
            obs_info[p] = { 'cat': 'General Disease Severity', 'descr': p, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }

        # ACS1-ACS5
        for n in range(1,6):
            p = 'ACS' + str(n) + 'prec'
            obs_info[p] = { 'cat': 'General Disease Severity', 'descr': p, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }

        # G1-G4
        for n in range(1,5):
            p = 'G' + str(n) + 'prec'
            obs_info[p] = { 'cat': 'General Disease Severity', 'descr': p, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }

        # SD1-SD4
        for n in range(1,5):
            p = 'SD' + str(n) + 'prec'
            obs_info[p] = { 'cat': 'General Disease Severity', 'descr': p, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }

        # SL1-SL5
        for n in range(1,6):
            p = 'SL' + str(n) + 'prec'
            obs_info[p] = { 'cat': 'General Disease Severity', 'descr': p, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }

        # NT1-NT6
        for n in range(1,7):
            p = 'NT' + str(n) + 'prec'
            obs_info[p] = { 'cat': 'General Disease Severity', 'descr': p, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }


        # EMA - handle all /.*score/
        obs_info['ATscore'] = { 'cat': 'General Disease Severity', 'descr': 'ATscore', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }
        obs_info['BTscore'] = { 'cat': 'General Disease Severity', 'descr': 'BTscore', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }
        
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
    name_index = {}
    for md in ATTRIBUTE_METADATA:
        abbrev = md['abbrev']
        name = md['name']
        if (abbrev in md_index) or (name in name_index):
            sys.stderr.write("FATAL - duplicate entry in ATTRIBUTE_METADATA, abbreviation=" + abbrev)
            sys.stderr.flush()
            sys.exit(1)
        md_index[abbrev] = md
        name_index[name] = md

    def get_attribute_metadata(varname, which):
        if varname in md_index:
            return md_index[varname][which].replace('\n', '')
        else:
            sys.stderr.write("WARN - couldn't find metadata entry for " + varname + "\n")
            sys.stderr.flush()
            return varname

    df['Label'] = df['SubjectVar'].apply(lambda x: get_attribute_metadata(x, 'name'))
    df['Description'] = df['SubjectVar'].apply(lambda x: get_attribute_metadata(x, 'descr'))

    return df
        
def add_scale_metadata(df):
    # index metadata by abbreviation
    smd_index = {}
    name_index = {}
    for md in SCALE_METADATA: 
       abbrev = md['abbrev']
       name = md['name']
       if (abbrev in smd_index) or (name in name_index):
           sys.stderr.write("FATAL - duplicate entry in SCALE_METADATA, abbreviation=" + abbrev + " label=" + name)
           sys.stderr.flush()
           sys.exit(1)
       smd_index[abbrev] = md
       name_index[name] = md

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
            sys.stderr.write("WARN - couldn't find metadata entry for " + testname + "\n")
            sys.stderr.flush()
            return testname

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
    pd.set_option('display.max_colwidth', None)
    
    # If the output dir is not specified then use the input dir
    if args.output_dir is None:
        args.output_dir = args.input_dir

    # Process the demographic variables
    df_demo = process_demographics(args.input_dir)
    df_demo_long = pd.melt(df_demo, id_vars=['SubjectNum'], var_name ='SubjectVar', value_name ='Value')
    df_demo_long = df_demo_long.dropna()

    # Mapping from SubjectNum to condate1
    subj_condates = {}
    for index, row in df_demo.iterrows():
        sn = row['SubjectNum']
        cd = row['condate1']
        if sn in subj_condates:
            sys.stderr.print("duplicate df_demo entry for SubjectNum=" + sn)
            sys.exit(1)
        subj_condates[sn] = cd
        
    df_long = process_longitudinal_data(os.path.join(args.input_dir, 'Longitudinal.csv'))
    df_all_vars = df_long

    # TODO - drop subjects not in df_long from df_demo
    
    pd.set_option('display.max_colwidth', None)

    # add VisitNum and sort
    df_all_vars["VisitNum"] = df_all_vars["VisitCode"].map(assign_VisitNumber)
    df_all_vars["VisitDate"] = df_all_vars["VisitCode"].map(assign_VisitDate)
    df_all_vars_sorted = df_all_vars.sort_values(by = ['SubjectNum', 'VisitNum'])

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
    filename = OUTPUT_PREFIX + "_projects.csv"
    fpath = os.path.join(args.output_dir, filename)
    with open(fpath, 'w') as fh:
        fh.write("project_name,project_description,primary_disease,study_name,longitudinal,study_description\n")
        fh.write("University of Iowa EMA,University of Iowa EMA patients,Hearing Loss," + EMA_STUDY + ",1,University of Iowa EMA Nov2020\n")
    files.append(["Project", filename])
    
    df_all_vars.sort_values(by = ['SubjectNum'])
    filename = OUTPUT_PREFIX + "_obs.csv"

    print("Writing " + filename)
    df_all_vars.to_csv(os.path.join(args.output_dir, filename), index = False)
    # pp.pprint(df_demo.sort_values(by = ['SubjectNum', 'Study']))
    demographics_filename = OUTPUT_PREFIX + "_demographics.csv"
    print("Writing " + demographics_filename)
    df_demo.to_csv(os.path.join(args.output_dir, demographics_filename), index = False)

    # pp.pprint(df_demo_long)
    filename = OUTPUT_PREFIX + "_demographics_long.csv"
    files.append(["Subject Info", filename])
    print("Writing " + filename)
    df_demo_long.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_all_vars_long_sorted)

    observations_filename = OUTPUT_PREFIX + "_obs_long.csv"
    files.append(["Observations", observations_filename])
    print("Writing " + filename)
    df_all_vars_long_sorted = df_all_vars_long_sorted.drop_duplicates()
    df_all_vars_long_sorted.to_csv(os.path.join(args.output_dir, observations_filename), index = False)

    # Print a table of visit information
    #
    # e.g., 
    # SubjectNum,VisitCode,VisitDate,VisitNum,Birthdate,AgeAtVisit
    # 3000,SC,2011-01-01,1,1941-12-01,69.1
    # 3000,BL,2011-02-01,2,1941-12-01,69.2
#    print("df_all_vars=")
#    print(df_all_vars)

    filename = OUTPUT_PREFIX + "_visit_info.csv"
    files.append(["Visit", filename])
    print("Writing " + filename)
    df_visits = df_all_vars.loc[:, ['SubjectNum','VisitCode','VisitNum','VisitDate']]
#    print("df_visits=")
#    print(df_visits)
    df_visits = df_visits.drop_duplicates()
    df_visits.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique observation variables in the data
    unique_obs = df_all_vars_long.Testname.unique()
    df_unique_obs = pd.DataFrame({"Testname": unique_obs}).sort_values(by = ['Testname'])
    # add scale metadata
    df_unique_obs = add_scale_metadata(df_unique_obs)
    filename = OUTPUT_PREFIX + "_unique_obs.csv"
    files.append(["Observation Ontology", filename])
    print("Writing " + filename)
    df_unique_obs.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique subject variables in the data
    df_unique_subject_vars = pd.DataFrame({"SubjectVar": df_demo_long.SubjectVar.unique()})
    # add scale metadata
    df_unique_subject_vars = add_attribute_metadata(df_unique_subject_vars)
    # pp.pprint(df_unique_subject_vars)
    filename = OUTPUT_PREFIX + "_unique_subject_vars.csv"
    files.append(["Subject Ontology", filename])
    print("Writing " + filename)
    df_unique_subject_vars.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Field mapping table
    df_field_mapping = generate_field_mapping(df_unique_subject_vars, df_unique_obs, demographics_filename, observations_filename)
    filename = OUTPUT_PREFIX + "_field_mapping.csv"
    print("Writing " + filename)
    df_field_mapping.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Files file
    filename = OUTPUT_PREFIX + "_files.csv";
    fpath = os.path.join(args.output_dir, filename)
    with open(fpath, 'w') as fh:
        fh.write("Entity,File\n");
        fh.write("\n".join([",".join(f) for f in files]) + "\n")
    
if __name__ == '__main__':
    main()
