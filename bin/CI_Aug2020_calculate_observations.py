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

def process_demographics(input_dir):

    demographics_filename = 'demo.csv'

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(os.path.join(input_dir, demographics_filename))
    
    # Recode some of the variables such as gender, race
    df_demo['Study'] = "University of Iowa CI"

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
                            "testdate": "VisitDate",
                            "BAITotalRaw": "Beck Anxiety Inventory"}, 
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
                            "testdate": "VisitDate",
                            "BDITotalRaw": "Beck Depression Index"}, 
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
                            "TotRecRaw": "BVMT Total Recall Raw",
                            "TotRecTscore": "BVMT Total Recall T Score",
                            "DelRecRaw": "BVMT Delayed Recall Raw",
                            "DelRecTscore": "BVMT Delayed Recall T Score",
                            'RecDiscrimIndexRaw': "BVMT Recall Discrimination Raw",
                            "RecDiscrimIndex%ile": "BVMT Recall Discrimination Percentile"},
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
                            "TotRecRaw": "HVLT Total Recall Raw",
                            "TotRecTscore": "HVLT Total Recall T Score",
                            "DelRecRaw": "HVLT Delayed Recall Raw",
                            "DelRecTscore": "HVLT Delayed Recall T Score",
                            "RecDiscrim IndexRaw": "HVLT Recall Discrimination Index Raw",
                            "RecDiscrim IndexTscore": "HVLT Recall Discrimination Index T Score",
                            "RetRaw": "HVLT Retention Raw",
                            "RetTscore": "HVLT Retention T Score"},
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
                            "testdate": "VisitDate"}, 
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
                            "SimRaw": "WAIS Similarities Raw",
                            "Sim SS": "WAIS Similarities Symbol Search",
                            "DigSp Raw": "WAIS Digit Span Raw",
                            "DigSp SS": "WAIS Digit Span Symbol Search",
                            "MatReas Raw": "WAIS Matrix Reasoning Raw",
                            "MatReas SS": "WAIS Matrix Reasoning Symbol Search"},
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
                            "SimRaw": "WRAT Similarities Raw",
                            "Sim SS": "WRAT Similarities Symbol Search"}, 
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
                            "testdate": "VisitDate",
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

    df = df.drop(['test_sess', 'AgeAtSession'], axis=1)

    print("NEO_FFI:")
    pp.pprint(df)
    return df

def generate_field_mapping(df_unique_subj_vars, df_unique_obs, demographics_file, observations_file):
    fmcols = ['Category','Scale','Database Entity','Ontology Label','Source File','Entry Type','FieldName','Testname','Type','Data Type','Flip Axis','Ordinal Sort']
    fmvals = []
    
    # process subject attributes
    for index, row in df_unique_subj_vars.iterrows():
        obs = row['Observations']
        stype = ''
        data_type = ''
        flip_axis=''
        ordinal_sort = ''

        if re.match(r'^Age\s.*$', obs):
            stype = 'Decimal'
            data_type = 'Continuous'
        elif re.match(r'^Date of.*$', obs):
            stype = 'Date'
            data_type = 'Continuous'
        elif re.match(r'^(Sex|Marital Status|ear\d|UIHC\d|Deceased|Type\d|Cause of|Study)', obs):
            stype = 'Char'
            data_type = 'Categorical'
            
        if stype == '':
            sys.stderr.write("Type/datatype could not be determined for " + obs + "\n")
            sys.stderr.flush()
            sys.exit(1)

        nr = ['Demographics','','subject_ontology',obs,demographics_file,'Property',obs,obs,stype,data_type,flip_axis,ordinal_sort]
        fmvals.append(nr)

        # subject_visit?
#        fmvals.append([SubjectVisit,,subject_visit,event_date,ppmi_visit_info.csv,Property,VisitDate,VisitDate,Date,Continuous,,])
#        SubjectVisit,,subject_visit,visit_event,ppmi_visit_info.csv,Property,VisitCode,VisitCode,Char,Ordinal,,"BL,PW,RS1,SC,ST,U01,V01,V02,V03,V04,V05,V06,V07,V08,V09,V10,V11,V12,V13,V14,V15,V16"
#        SubjectVisit,,subject_visit,visit_num,ppmi_visit_info.csv,Property,VisitNumber,VisitNumber,Integer,Ordinal,,

    # process observation variables
    for index, row in df_unique_obs.iterrows():
        obs = row['Observations']

        if re.match(r'^Visit.*$', obs):
            continue

        obs_info = {

            # Trails - Trail Making Test - neuropsychological test of visual attention and task switching
            'A SS': { 'cat': 'Cognitive', 'descr': 'Trails Part A SS', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'A Seconds to Complete' : { 'cat': 'Cognitive', 'descr': 'Trails Part A Seconds to Complete', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'A T-score': { 'cat': 'Cognitive', 'descr': 'Trails Part A T-score', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'B SS': { 'cat': 'Cognitive', 'descr': 'Trails Part B SS', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'B Seconds to Complete' : { 'cat': 'Cognitive', 'descr': 'Trails Part B Seconds to Complete', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            'B T-score': { 'cat': 'Cognitive', 'descr': 'Trails Part B T-score', 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # BVMT - Brief Visuospatial Memory Test
            
            "BVMT Total Recall Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT Total Recall T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT Delayed Recall Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT Delayed Recall T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT Recall Discrimination Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "BVMT Recall Discrimination Percentile" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' },
            
            # HVLT - Hopkins Verbal Learning Test
            "HVLT Total Recall Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT Total Recall T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT Delayed Recall Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT Delayed Recall T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT Recall Discrimination Index Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT Recall Discrimination Index T Score" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT Retention Raw": { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "HVLT Retention T Score": { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # BAI - Beck Anxiety Inventory
            "Beck Anxiety Inventory" : { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # BDI - Beck Depression Index
            "Beck Depression Index" : { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # WAIS - Processing Wechsler Adult Intelligence Scale IV
            "WAIS Similarities Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS Similarities Symbol Search" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS Digit Span Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS Digit Span Symbol Search" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS Matrix Reasoning Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WAIS Matrix Reasoning Symbol Search" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },

            # WRAT - Wide Range Achievement Test IV
            "WRAT Similarities Raw" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
            "WRAT Similarities Symbol Search" : { 'cat': 'Cognitive', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' },
        }

        # Neo Five Factor Inventory Personality Test
        neo_ff_factors = [
            { 'short': 'Neu', 'long': 'Neuroticism' },
            { 'short': 'Extro', 'long': 'Extraversion' },
            { 'short': 'Open', 'long': 'Openness' },
            { 'short': 'Agree', 'long': 'Agreeableness' },
            { 'short': 'Consci', 'long': 'Conscientiousness' }
        ]

        for f in ['Neuroticism', 'Extraversion', 'Openness', 'Agreeableness', 'Conscientiousness']:
            obs_info[f + ' Raw Score'] = { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }
            obs_info[f + ' Rank'] = { 'cat': 'Mental Health', 'descr': None, 'type': 'Char', 'data_type': 'Categorical', 'flip_axis': 0, 'ordinal_sort': '' }
            obs_info[f + ' T Score'] = { 'cat': 'Mental Health', 'descr': None, 'type': 'Decimal', 'data_type': 'Continuous', 'flip_axis': 0, 'ordinal_sort': '' }

            
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
    
    print("Generating summary information")
    df_groups_with_multiple = df_all_vars_long_sorted.groupby(['SubjectNum', 'Testname']).filter(lambda x: len(x) > 1)

    # Once the dataframes are created write the table to a CSV file
    # pp.pprint(df_pilot_bio.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))

    df_all_vars.sort_values(by = ['SubjectNum'])
    filename = "UI_CI_obs.csv"
    print("Writing " + filename)
    df_all_vars.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_demo.sort_values(by = ['SubjectNum', 'Study']))
    demographics_filename = "UI_CI_demographics.csv"
    print("Writing " + demographics_filename)
    df_demo.to_csv(os.path.join(args.output_dir, demographics_filename), index = False)

    # pp.pprint(df_demo_long)
    filename = "UI_CI_demographics_long.csv"
    print("Writing " + filename)
    df_demo_long.to_csv(os.path.join(args.output_dir, filename), index = False)

    # pp.pprint(df_all_vars_long_sorted)
    observations_filename = "UI_CI_obs_long.csv"
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
    filename = "UI_CI_visit_info.csv"
    print("Writing " + filename)
    df_visits.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique observation variables in the data
    unique_obs = df_all_vars_long.Testname.unique()
    df_unique_obs = pd.DataFrame({"Observations": unique_obs}).sort_values(by = ['Observations'])
    filename = "UI_CI_unique_obs.csv"
    print("Writing " + filename)
    df_unique_obs.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Print a table of unique subject variables in the data
    df_unique_subject_vars = pd.DataFrame({"Observations": df_demo_long.SubjectVar.unique()})
    # pp.pprint(df_unique_subject_vars)
    filename = "UI_CI_unique_subject_vars.csv"
    print("Writing " + filename)
    df_unique_subject_vars.to_csv(os.path.join(args.output_dir, filename), index = False)

    # Field mapping table
    df_field_mapping = generate_field_mapping(df_unique_subject_vars, df_unique_obs, demographics_filename, observations_filename)
    filename = "UI_CI_field_mapping.csv"
    print("Writing " + filename)
    df_field_mapping.to_csv(os.path.join(args.output_dir, filename), index = False)
     
if __name__ == '__main__':
    main()
