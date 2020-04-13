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
import sys
import pandas as pd
import numpy as np
import pprint
import datetime as dt

scale_file_map = {'CNC_word': "UI_cochlear_CNC.csv",
                   'CNC_phoneme': "UI_cochlear_CNC.csv",
                   'edu': "UI_cochlear_edu.csv",
                   'AzBio' : "UI_cochlear_AzBio.csv",
                   'BAI' : "UI_cochlear_BAI.csv",
                   'BDI' : "UI_cochlear_BDI.csv",
                   'BVMT' : "UI_cochlear_BVMT.csv",
                   'HVLT' : "UI_cochlear_HVLT.csv",
                   'NEO_FFI': "UI_cochlear_NEO-FFI.csv",
                   'Trails': "UI_cochlear_Trails.csv",
                   'WAIS': "UI_cochlear_WAIS.csv",
                   'WRAT': 'UI_cochlear_WRAT.csv'
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

def assign_maritalStatus(row):
    if (row['maritalStatus'] == 1):
        return "Married"
    elif (row['maritalStatus'] == 2):
        return "Single"
    elif (row['maritalStatus'] == 3):
        return "Divorced"
    elif (row['maritalStatus'] == 4):
        return "Widowed"
    else:
        return "Unknown Marital Status"
    
def assign_Deceased(row):
    if (row['Deceased'] == 1):
        return "Alive"
    if (row['Deceased'] == 2):
        return "Deceased"
    else:
        return "Unknown Status"

def process_demographics(input_dir):

    demographics_filename = 'UI_cochlear_demo.csv'

    # Read the input as a pandas dataframe
    df_demo = pd.read_csv(input_dir + demographics_filename)

    # Subset the frame for the columns needed
    df_demo = df_demo.loc[:, ['SID', "ImplantAgeYrs1","gender", "maritalStatus", "YrsEdu", "Deceased", "opdate1", "condate1", "opdate2", "condate2", "opdate3", "condate3", 
                            "lAgeDeaf", "rAgeDeaf", "ear1", "ear2", "ear3", "Type1", "Type2", "Type3", "lPhysCauseLoss", "rPhysCauseLoss", "lAgeAidUse", "rAgeAidUse"]]

    # Recode some of the variables such as gender, race
    df_demo['Study'] = "University of Iowa Cochlear Implant Patients"
    df_demo["maritalStatus"] = df_demo[["maritalStatus"]].apply(assign_maritalStatus, axis = 1)
    df_demo['gender'] = df_demo['gender'].map(lambda x: 'Male' if x == "M" else 'Female')
    #pp.pprint(df_demo)
    #pp.pprint(df_demo["Deceased"])

    df_demo["Deceased"] = df_demo[["Deceased"]].apply(assign_Deceased, axis = 1)
    
    # Process some of the dates to assume the first of the month allow date operations
    # and then convert the datetime string to date
    df_demo[["opdate1", "condate1", "opdate2", "condate2", "opdate3", "condate3"]] = df_demo[["opdate1", "condate1", "opdate2", "condate2", "opdate3", "condate3"]].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d', errors='coerce'))

    # Calculate some of the numeric properties such as age at enrollemnt, age at diagnosis
    df_demo['Age At Connection 1'] = round(((df_demo['condate1'] - df_demo['opdate1']).dt.days/365.25) + df_demo['ImplantAgeYrs1']) 
    df_demo['Age At Operation 2'] = round(((df_demo['opdate2'] - df_demo['opdate1']).dt.days/365.25) + df_demo['ImplantAgeYrs1']) 
    df_demo['Age At Connection 2'] = round(((df_demo['condate2'] - df_demo['opdate1']).dt.days/365.25) + df_demo['ImplantAgeYrs1']) 
    df_demo['Age At Operation 3'] = round(((df_demo['opdate3'] - df_demo['opdate1']).dt.days/365.25) + df_demo['ImplantAgeYrs1']) 
    df_demo['Age At Connection 3'] = round(((df_demo['condate3'] - df_demo['opdate1']).dt.days/365.25) + df_demo['ImplantAgeYrs1'])
    #pp.pprint(df_demo)
    #exit()

    df_demo = df_demo.rename(columns={"SID": "SubjectNum", 
                            "ImplantAgeYrs1": "Age At Operation 1", 
                            "gender": "Sex",
                            "maritalStatus": "Marital Status",
                            "YrsEdu": "Years of Education",
                            "opdate1": "Date of Operation 1",
                            "condate1": "Date of Connection 1",
                            "opdate2": "Date of Operation 2",
                            "condate2": "Date of Connection 2",
                            "opdate3": "Date of Operation 3",
                            "condate3": "Date of Connection 3",
                            "Deceased": "Status",
                            "lAgeDeaf": "Age of Deafness Left Ear",
                            "rAgeDeaf": "Age of Deafness Right Ear",
                            "rPhysCauseLoss": "Cause of Right Sided Hearing Loss",
                            "lPhysCauseLoss": "Cause of Left Sided Hearing Loss",
                            "lAgeAidUse": "Age at Left Hearing Aid Use",
                            "rAgeAidUse": "Age at Right Hearing Aid Use"}, 
                            errors="raise")

    return df_demo
    pp.pprint(df_demo)
    #exit()

def process_YrsEdu(filename):

    df['YrsEdu'] = df.loc[:, ['SID','YrsEdu']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID','YrsEdu']]
    df = df.groupby(['SID']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "YrsEdu": "Years of Education"}, 
                            errors="raise")

def assign_Amplification(row):
    if (row['AmplificationRight'] == 1) and (row["AmplificationLeft"] == 1):
        return "No hearing amplification"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 1):
        return "Right sided hearing aid only"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 1):
        return "Right sided cochlear implant only"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 2):
        return "Left sided hearing aid only"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 3):
        return "Left sided cochlear implant only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 2):
        return "Bilateral hearing aids"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 3):
        return "Right sided hearing aid, left sided cochlear implant"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 2):
        return "Right sided cochlear implant, left sided hearing aid"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 3):
        return "Bilateral cochlear implants"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 1):
        return "Right sided natural acoustic only"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 2):
        return "Right sided natural acoustic, left sided hearing aid"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 3):
        return "Right sided natural acoustic, left sided cochlear implant"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 4):
        return "Bilateral natural acoustic"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 1):
        return "Right sided cochlear implant and hearing aid only"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 2):
        return "Right sided cochlear implant and hearing aid, left sided hearing aid"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 3:
        return "Right sided cochlear implant and hearing aid, left sided cochlear implant"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 4):
        return "Right sided cochlear implant and hearing aid, left sided natural acoustic"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 5):
        return "Right sided cochlear implant and hearing aid, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 5):
        return "Left sided cochlear implant and hearing aid only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 5):
        return "Right sided hearing aid, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 5):
        return "Right sided cochlear implant, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 5):
        return "Right sided natural acoustic, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 1):
        return "Right sided natural acoustic and cochlear implant only"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 2):
        return "Right sided natural acoustic and cochlear implant, left sided hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 3):
        return "Right sided natural acoustic and cochlear implant, left sided cochlear implant"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 4):
        return "Right sided natural acoustic and cochlear implant, left sided natural acoustic"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 5):
        return "Right sided natural acoustic and cochlear implant, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 6):
        return "Bilateral natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 6):
        return "Left sided natural acoustic and cochlear implant only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 6):
        return "Rigth sided hearing aid, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 6):
        return "Right sided cochlear implant, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 6):
        return "Right sided natural acoustic, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 6):
        return "Right sided cochlear implant and hearing aid, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 1):
        return "Right sided CROS only"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 2):
        return "Right sided CROS, left sided hearing aid"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 3):
        return "Right sided CROS, left sided cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 4):
        return "Right sided CROS, left sided natural acoustic"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 5):
        return "Right sided CROS, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 6):
        return "Right sided CROS, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 7):
        return "Bilateral CROS"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 7):
        return "Left sided CROS only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 7):
        return "Right sided hearing aid, left sided CROS"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 7):
        return "Right sided cochlear implant, left sided CROS"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 7):
        return "Right sided natural acoustic, left sided CROS"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 7):
        return "Right sided cochlear implant and hearing aid, left sided CROS"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 7):
        return "Right sided natural acoustic and cochlear implant, left sided CROS"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 1):
        return "Right sided BAHA only"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 2):
        return "Right sided BAHA, left sided hearing aid"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 3):
        return "Right sided BAHA, left sided cochlear implant"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 4):
        return "Right sided BAHA, left sided natural acoustic"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 5):
        return "Right sided BAHA, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 6):
        return "Right sided BAHA, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 7):
        return "Right sided BAHA, left sided CROS"
    if (row["AmplificationRight"] == 8) and row (row["AmplificationLeft"] == 8):
        return "Bilateral BAHAs"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 8):
        return "Left sided BAHA only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 8):
        return "Right sided hearing aid, left sided BAHA"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 8):
        return "Right sided cochlear implant, left sided BAHA"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 8):
        return "Right sided natural acoustic, left sided BAHA"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 8):
        return "Right sided cochlear implant and hearing aid, left sided BAHA"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 8):
        return "Right sided natural acoustic and cochlear implant, left sided BAHA"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 8):
        return "Right sided CROS, left sided BAHA"
    else:
        return "Unknown amplification"

def process_CNC_word(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['CNC'] = df.loc[:, ['SID','PostIntervention', 'DateCreated', 'AmplificationLeft', 'AmplificationRight', 'CncWord_Percent']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID','PostIntervention', 'DateCreated', 'AmplificationLeft', 'AmplificationRight', 'CncWord_Percent']]
    df['Amplification'] = df_demo[["AmplificationRight", "AmplificationLeft"]].apply(assign_amplification, axis = 1)
    df["DateCreated"] = df["DateCreated"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'PostIntervention', 'DateCreated']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "Post Intervention": "Months since Cochlear Implantation", 
                            "DateCreated": "Visit Date",
                            "AmplificationLeft": "Type of Amplification Left Ear",
                            "AmplificationRight": "Type of Amplification Right Ear",
                            "CncWord_Percent": "CNC Word Percentage Correct"}, 
                            errors="raise")
    pp.pprint(df)
    return df
    

def assign_Amplification(row):
    if (row['AmplificationRight'] == 1) and (row["AmplificationLeft"] == 1):
        return "No hearing amplification"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 1):
        return "Right sided hearing aid only"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 1):
        return "Right sided cochlear implant only"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 2):
        return "Left sided hearing aid only"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 3):
        return "Left sided cochlear implant only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 2):
        return "Bilateral hearing aids"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 3):
        return "Right sided hearing aid, left sided cochlear implant"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 2):
        return "Right sided cochlear implant, left sided hearing aid"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 3):
        return "Bilateral cochlear implants"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 1):
        return "Right sided natural acoustic only"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 2):
        return "Right sided natural acoustic, left sided hearing aid"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 3):
        return "Right sided natural acoustic, left sided cochlear implant"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 4):
        return "Bilateral natural acoustic"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 1):
        return "Right sided cochlear implant and hearing aid only"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 2):
        return "Right sided cochlear implant and hearing aid, left sided hearing aid"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 3:
        return "Right sided cochlear implant and hearing aid, left sided cochlear implant"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 4):
        return "Right sided cochlear implant and hearing aid, left sided natural acoustic"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 5):
        return "Right sided cochlear implant and hearing aid, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 5):
        return "Left sided cochlear implant and hearing aid only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 5):
        return "Right sided hearing aid, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 5):
        return "Right sided cochlear implant, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 5):
        return "Right sided natural acoustic, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 1):
        return "Right sided natural acoustic and cochlear implant only"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 2):
        return "Right sided natural acoustic and cochlear implant, left sided hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 3):
        return "Right sided natural acoustic and cochlear implant, left sided cochlear implant"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 4):
        return "Right sided natural acoustic and cochlear implant, left sided natural acoustic"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 5):
        return "Right sided natural acoustic and cochlear implant, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 6):
        return "Bilateral natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 6):
        return "Left sided natural acoustic and cochlear implant only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 6):
        return "Rigth sided hearing aid, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 6):
        return "Right sided cochlear implant, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 6):
        return "Right sided natural acoustic, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 6):
        return "Right sided cochlear implant and hearing aid, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 1):
        return "Right sided CROS only"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 2):
        return "Right sided CROS, left sided hearing aid"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 3):
        return "Right sided CROS, left sided cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 4):
        return "Right sided CROS, left sided natural acoustic"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 5):
        return "Right sided CROS, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 6):
        return "Right sided CROS, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 7):
        return "Bilateral CROS"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 7):
        return "Left sided CROS only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 7):
        return "Right sided hearing aid, left sided CROS"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 7):
        return "Right sided cochlear implant, left sided CROS"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 7):
        return "Right sided natural acoustic, left sided CROS"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 7):
        return "Right sided cochlear implant and hearing aid, left sided CROS"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 7):
        return "Right sided natural acoustic and cochlear implant, left sided CROS"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 1):
        return "Right sided BAHA only"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 2):
        return "Right sided BAHA, left sided hearing aid"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 3):
        return "Right sided BAHA, left sided cochlear implant"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 4):
        return "Right sided BAHA, left sided natural acoustic"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 5):
        return "Right sided BAHA, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 6):
        return "Right sided BAHA, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 7):
        return "Right sided BAHA, left sided CROS"
    if (row["AmplificationRight"] == 8) and row (row["AmplificationLeft"] == 8):
        return "Bilateral BAHAs"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 8):
        return "Left sided BAHA only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 8):
        return "Right sided hearing aid, left sided BAHA"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 8):
        return "Right sided cochlear implant, left sided BAHA"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 8):
        return "Right sided natural acoustic, left sided BAHA"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 8):
        return "Right sided cochlear implant and hearing aid, left sided BAHA"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 8):
        return "Right sided natural acoustic and cochlear implant, left sided BAHA"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 8):
        return "Right sided CROS, left sided BAHA"
    else:
        return "Unknown amplification"

def process_CNC_phoneme(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    df['CNC'] = df.loc[:, ['SID','PostIntervention', 'DateCreated', 'AmplificationLeft', 'AmplificationRight', 'CncPhon_Percent']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID','PostIntervention', 'DateCreated', 'AmplificationLeft', 'AmplificationRight', 'CncPhon_Percent']]
    df["DateCreated"] = df["DateCreated"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Amplification'] = df_demo[["AmplificationRight", "AmplificationLeft"]].apply(assign_amplification, axis = 1)

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'PostIntervention', 'DateCreated']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "Post Intervention": "Months since Cochlear Implantation", 
                            "DateCreated": "Visit Date",
                            "CncPhon_Percent": "CNC Phoneme Percentage Correct"}, 
                            errors="raise")
    pp.pprint(df)
    return df
    #pp.pprint(df)
    exit()

def assign_Amplification(row):
    if (row['AmplificationRight'] == 1) and (row["AmplificationLeft"] == 1):
        return "No hearing amplification"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 1):
        return "Right sided hearing aid only"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 1):
        return "Right sided cochlear implant only"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 2):
        return "Left sided hearing aid only"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 3):
        return "Left sided cochlear implant only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 2):
        return "Bilateral hearing aids"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 3):
        return "Right sided hearing aid, left sided cochlear implant"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 2):
        return "Right sided cochlear implant, left sided hearing aid"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 3):
        return "Bilateral cochlear implants"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 1):
        return "Right sided natural acoustic only"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 2):
        return "Right sided natural acoustic, left sided hearing aid"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 3):
        return "Right sided natural acoustic, left sided cochlear implant"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 4):
        return "Bilateral natural acoustic"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 1):
        return "Right sided cochlear implant and hearing aid only"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 2):
        return "Right sided cochlear implant and hearing aid, left sided hearing aid"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 3:
        return "Right sided cochlear implant and hearing aid, left sided cochlear implant"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 4):
        return "Right sided cochlear implant and hearing aid, left sided natural acoustic"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 5):
        return "Right sided cochlear implant and hearing aid, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 5):
        return "Left sided cochlear implant and hearing aid only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 5):
        return "Right sided hearing aid, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 5):
        return "Right sided cochlear implant, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 5):
        return "Right sided natural acoustic, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 1):
        return "Right sided natural acoustic and cochlear implant only"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 2):
        return "Right sided natural acoustic and cochlear implant, left sided hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 3):
        return "Right sided natural acoustic and cochlear implant, left sided cochlear implant"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 4):
        return "Right sided natural acoustic and cochlear implant, left sided natural acoustic"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 5):
        return "Right sided natural acoustic and cochlear implant, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 6):
        return "Bilateral natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 6):
        return "Left sided natural acoustic and cochlear implant only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 6):
        return "Rigth sided hearing aid, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 6):
        return "Right sided cochlear implant, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 6):
        return "Right sided natural acoustic, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 6):
        return "Right sided cochlear implant and hearing aid, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 1):
        return "Right sided CROS only"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 2):
        return "Right sided CROS, left sided hearing aid"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 3):
        return "Right sided CROS, left sided cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 4):
        return "Right sided CROS, left sided natural acoustic"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 5):
        return "Right sided CROS, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 6):
        return "Right sided CROS, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 7):
        return "Bilateral CROS"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 7):
        return "Left sided CROS only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 7):
        return "Right sided hearing aid, left sided CROS"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 7):
        return "Right sided cochlear implant, left sided CROS"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 7):
        return "Right sided natural acoustic, left sided CROS"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 7):
        return "Right sided cochlear implant and hearing aid, left sided CROS"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 7):
        return "Right sided natural acoustic and cochlear implant, left sided CROS"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 1):
        return "Right sided BAHA only"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 2):
        return "Right sided BAHA, left sided hearing aid"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 3):
        return "Right sided BAHA, left sided cochlear implant"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 4):
        return "Right sided BAHA, left sided natural acoustic"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 5):
        return "Right sided BAHA, left sided cochlear implant and hearing aid"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 6):
        return "Right sided BAHA, left sided natural acoustic and cochlear implant"
    if (row["AmplificationRight"] == 8) and (row["AmplificationLeft"] == 7):
        return "Right sided BAHA, left sided CROS"
    if (row["AmplificationRight"] == 8) and row (row["AmplificationLeft"] == 8):
        return "Bilateral BAHAs"
    if (row["AmplificationRight"] == 1) and (row["AmplificationLeft"] == 8):
        return "Left sided BAHA only"
    if (row["AmplificationRight"] == 2) and (row["AmplificationLeft"] == 8):
        return "Right sided hearing aid, left sided BAHA"
    if (row["AmplificationRight"] == 3) and (row["AmplificationLeft"] == 8):
        return "Right sided cochlear implant, left sided BAHA"
    if (row["AmplificationRight"] == 4) and (row["AmplificationLeft"] == 8):
        return "Right sided natural acoustic, left sided BAHA"
    if (row["AmplificationRight"] == 5) and (row["AmplificationLeft"] == 8):
        return "Right sided cochlear implant and hearing aid, left sided BAHA"
    if (row["AmplificationRight"] == 6) and (row["AmplificationLeft"] == 8):
        return "Right sided natural acoustic and cochlear implant, left sided BAHA"
    if (row["AmplificationRight"] == 7) and (row["AmplificationLeft"] == 8):
        return "Right sided CROS, left sided BAHA"
    else:
        return "Unknown amplification"

def assign_condition(row):
    if (row["Condition"] == 1):
        return "Quiet"
    if (row["Condition"] == 2):
        return "5 decibles louder than sound from the front"
    if (row["Condition"] == 3):
        return "10 decibles louder than sound from the front"
    if (row["Condition"] == 4):
        return "10 decibles louder than sound from the left"
    if (row["Condition"] == 5):
        return "10 decibles louder than sound from the right"
    if (row["Condition"] == 6):
        return "10 decibles louder than sound from the back"
    if (row["Condition"] == "-3 SNR from Front"):
        return "3 decibles softer than sound"
    if (row["Condition"] == "-3 SNR from Right"):
        return "3 decibles softer than sound"
    if (row["Condition"] == "-3 SNR from Left"):
        return "3 decibles softer than sound"
    else:
        return "Unknown testing condition"

def process_AZBio(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['AZBio'] = df.loc[:, ['SID','PostIntervention', 'DateCreated', 'AmplificationLeft', 'AmplificationRight', "AzBioWord_Percent", "Condition"]].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID','PostIntervention', 'DateCreated', 'AmplificationLeft', 'AmplificationRight', "AzBioWord_Percent", "Condition"]]
    df["DateCreated"] = df["DateCreated"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df['Amplification'] = df_demo[["AmplificationRight", "AmplificationLeft"]].apply(assign_amplification, axis = 1)
    df["Condition"] = df[["Condition"]].apply(assign_condition)

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'PostIntervention', 'DateCreated']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "Post Intervention": "Months since Cochlear Implantation", 
                            "DateCreated": "Visit Date",
                            "AmplificationLeft": "Type of Amplification Left Ear",
                            "AmplificationRight": "Type of Amplification Right Ear",
                            "AzBioWord_Percent": "AZBio Percentage Correct"}, 
                            errors="raise")
    return df


def process_BAI(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BAI'] = df.loc[:, ['SID', 'testdate', 'TotalRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'TotalRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotalRaw": "Beck Anxiety Inventory"}, 
                            errors="raise")
    return df

def process_BDI(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BAI'] = df.loc[:, ['SID', 'testdate', 'TotalRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'TotalRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotalRaw": "Beck Depression Index"}, 
                            errors="raise")
    return df

def process_BVMT_total(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BVMT'] = df.loc[:, ['SID', 'testdate', 'TotRecRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'TotRecRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotRecRaw": "Total Recall Raw"}, 
                            errors="raise")
    return df

def process_BVMT_total_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BVMT'] = df.loc[:, ['SID', 'testdate', 'TotRecTscore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'TotRecTscore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotRecTscore": "Total Recall T Score"}, 
                            errors="raise")
    return df

def process_BVMT_delay(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BVMT'] = df.loc[:, ['SID', 'testdate', 'DelRecRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'DelRecRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "DelRecRaw": "Delayed Recall Raw"}, 
                            errors="raise")
    return df

def process_BVMT_delay_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BVMT'] = df.loc[:, ['SID', 'testdate', 'DelRecTscore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'DelRecTscore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "DelRecTscore": "Delayed Recall T Score"}, 
                            errors="raise")
    return df

def process_BVMT(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BVMT'] = df.loc[:, ['SID', 'testdate', 'RecDiscrimIndexRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'RecDiscrimIndexRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            'RecDiscrimIndexRaw': 'Recall Discrimination Raw'}, 
                            errors="raise")
    return df

def assign_RecDiscrimIndexpercent(row):
    if RecDiscrimIndexpercent == ">16":
        return "greater than 16%"
    if RecDiscrimIndexpercent == "11--16":
        return "11-16%"
    if RecDiscrimIndexpercent == "6--10":
        return "6-10%"
    if RecDiscrimIndexpercent == "3--5":
        return "3-5%"
    if RecDiscrimIndexpercent == "1--2":
        return "1-2%"
    if RecDiscrimIndexpercent == ">6":
        return "greater than 6%"

def process_BVMT_percent(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['BVMT'] = df.loc[:, ['SID', 'testdate', 'RecDiscrimIndexpercent']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'RecDiscrimIndexpercent']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))
    df["RecDiscrimIndexpercent"] = df["RecDiscrimIndexpercent"].apply(assign_RecDiscrimIndexpercent, axis = 1)

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "RecDiscrimIndexpercent": "Recall Discrimination Percent"}, 
                            errors="raise")
    return df

def process_HVLT_total(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'TotRecRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'TotRecRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotRecRaw": "Total Recall Raw"}, 
                            errors="raise")
    return df

def process_HVLT_total_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'TotRecTscore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'TotRecTscore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "TotRecTscore": "Total Recall T Score"}, 
                            errors="raise")
    return df

def process_HVLT_delayed(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'DelRecRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'DelRecRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "DelRecRaw": "Delayed Recall Raw"}, 
                            errors="raise")
    return df

def process_HVLT_delay_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'DelRecTscore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'DelRecTscore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "DelRecTscore": "Delayed Recall T Score"}, 
                            errors="raise")
    return df

def process_HVLT_discrim(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'RecDiscrim IndexRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'RecDiscrim IndexRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            'RecDiscrim IndexRaw': 'Recall Discrimination Raw'}, 
                            errors="raise")
    return df

def process_HVLT_discrim_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'RecDiscrim IndexTscore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'RecDiscrim IndexTscore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "RecDiscrim IndexTscore": "Recall Discrimination T Score"}, 
                            errors="raise")
    return df

def process_HVLT_retention(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'RetRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'RetRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "RetRaw": "Retention Raw"}, 
                            errors="raise")
    return df

def process_HVLT_retention_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['HVLT'] = df.loc[:, ['SID', 'testdate', 'RetTscore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'RetTscore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "RetTscore": "Retention T Score"}, 
                            errors="raise")
    return df

def process_Trails_a_seconds(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['Trails'] = df.loc[:, ['SID', 'testdate', 'A Seconds to Complete']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'A Seconds to Complete']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date"}, 
                            errors="raise")
    return df

def process_Trails_a_ss(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['Trails'] = df.loc[:, ['SID', 'testdate', 'A SS']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'A SS']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date"}, 
                            errors="raise")
    return df

def process_Trails_a_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['Trails'] = df.loc[:, ['SID', 'testdate', 'A T-score']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'A T-score']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date"}, 
                            errors="raise")
    return df

def process_Trails_b_seconds(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['Trails'] = df.loc[:, ['SID', 'testdate', 'B Seconds to Complete']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'B Seconds to Complete']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date"}, 
                            errors="raise")
    return df

def process_Trails_b_ss(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['Trails'] = df.loc[:, ['SID', 'testdate', 'B SS']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'B SS']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date"}, 
                            errors="raise")
    return df

def process_Trails_b_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['Trails'] = df.loc[:, ['SID', 'testdate', 'B T-score']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'B T-score']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date"}, 
                            errors="raise")
    return df

def process_WAIS_simularities(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WAIS'] = df.loc[:, ['SID', 'testdate', 'SimRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'SimRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "SimRaw": "Simularities Raw"}, 
                            errors="raise")
    return df

def process_WAIS_simularities_symbol(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WAIS'] = df.loc[:, ['SID', 'testdate', 'Sim SS']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'Sim SS']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "Sim SS": "Simularities Symbol Search"}, 
                            errors="raise")
    return df

def process_WAIS_digit(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WAIS'] = df.loc[:, ['SID', 'testdate', 'DigSp Raw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'DigSp Raw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "DigSp Raw": "Digit Span Raw"}, 
                            errors="raise")
    return df

def process_WAIS_digit_symbol(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WAIS'] = df.loc[:, ['SID', 'testdate', 'DigSp SS']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'DigSp SS']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "DigSp SS": "Digit Span Symbol Search"}, 
                            errors="raise")
    return df

def process_WAIS_matrix(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WAIS'] = df.loc[:, ['SID', 'testdate', 'MatReas Raw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'MatReas Raw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            'MatReas Raw': 'Matrix Reasoning Raw'}, 
                            errors="raise")
    return df


def process_WRAT_simularities(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'SimRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'SimRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "SimRaw": "Simularities Raw"}, 
                            errors="raise")
    return df

def process_WRAT_simularities_symbol(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'Sim SS']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'Sim SS']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "Sim SS": "Simularities Symbol Search"}, 
                            errors="raise")
    return df

def process_NEO_FFI_neu(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'NeuRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'NeuRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "NeuRaw": "Neuroticism Raw Score"}, 
                            errors="raise")
    return df

def process_NEO_FFI_neu_rank(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'NeuRank']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'NeuRank']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "NeuRank": "Neuroticism Rank"}, 
                            errors="raise")
    return df

def process_NEO_FFI_neu_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'NeuTScore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'NeuTScore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "NeuTScore": "Neuroticism T Score"}, 
                            errors="raise")
    return df

def process_NEO_FFI_extro(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'ExtroRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'ExtroRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "ExtroRaw": "Extraversion Raw Score"}, 
                            errors="raise")
    return df

def process_NEO_FFI_extro_rank(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'ExtroRank']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'ExtroRank']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "ExtroRank": "Extraversion Rank"}, 
                            errors="raise")
    return df

def process_NEO_FFI_extro_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'ExtroTScore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'ExtroTScore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "ExtroTScore": "Extraversion T Score"}, 
                            errors="raise")
    return df

def process_NEO_FFI_open(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'OpenRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'OpenRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "OpenRaw": "Openness Raw Score"}, 
                            errors="raise")
    return df

def process_NEO_FFI_open_rank(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'OpenRank']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'OpenRank']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "OpenRank": "Openness Rank"}, 
                            errors="raise")
    return df

def process_NEO_FFI_open_tscore(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'OpenTScore']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'OpenTScore']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "OpenTScore": "Openness T Score"}, 
                            errors="raise")
    return df

def process_NEO_FFI_agree(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'AgreeRaw']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'AgreeRaw']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "AgreeRaw": "Agreeableness Raw Score"}, 
                            errors="raise")
    return df

def process_NEO_FFI_agree_rank(filename):
    # Read the input as a pandas dataframe
    df = pd.read_csv(filename)
    # pp.pprint(df)
    df['WRAT'] = df.loc[:, ['SID', 'testdate', 'AgreeRank']].sum(axis=1, skipna = False) 
    df = df.loc[:, ['SID', 'testdate', 'AgreeRank']]
    df["testdate"] = df["testdate"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%y', errors='coerce'))

    # Some times there seem to be multiple rows for the same event and date. In such situations we are
    # arbitrarily deciding to use the first one that appears
    df = df.groupby(['SID', 'testdate']).first().reset_index()
    df = df.rename(columns={"SID": "SubjectNum", 
                            "testdate": "Visit Date",
                            "AgreeRank": "Agreeableness Rank"}, 
                            errors="raise")
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
    df_test = df_demo
    #pd.to_datetime(df_test['Enroll Date']).apply(lambda x: x.date()) 
    df_demo_long = pd.melt(df_test, id_vars=['SubjectNum'], var_name ='SubjectVar', value_name ='Value')
    df_demo_long = df_demo_long.dropna()

    # Cycle through the scales and calculate the totals or any other transformations that need to be made
    for scale, filename in scale_file_map.items():
        if (scale == 'CNC'):
            print("Processing Consonants Nucleus Consonants Test")
            df_CNC = process_CNC(args.input_dir + filename)
            # pp.pprint(df_semantic_fluency.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'AzBio'):
            print("Processing AzBio Sentence Test")
            df_AzBio = process_AzBio(args.input_dir + filename)
            # pp.pprint(df_benton_judgement.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'BAI'):
            print("Processing Beck Anxiety Inventory")
            df_BAI = process_BAI(args.input_dir + filename)
            # pp.pprint(df_mds_updrs1_1.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'BDI'):
            print("Processing Beck Depression Index")
            df_BDI = process_BDI(args.input_dir + filename)
            # pp.pprint(df_mds_updrs1_2.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'BVMT'):
            print("Processing Brief Visuospatial Memory Test")
            df_BVMT = process_BVMT(args.input_dir + filename)
            # pp.pprint(df_mds_updrs2.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'HVLT'):
            print("Processing Hopkins Verbal Learning Test")
            df_HVLT = process_HVLT(args.input_dir + filename)
            # pp.pprint(df_mds_updrs3.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'Trails'):
            print("Processing Trails")
            df_Trails = process_Trails(args.input_dir + filename)
            # pp.pprint(df_moca.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'WAIS'):
            print("Processing Wechsler Adult Intelligence Scale IV")
            df_WAIS =  process_WAIS(args.input_dir + filename)
            # pp.pprint(df_lns.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'WRAT'):
            print("Processing Wide Range Achievement Test IV")
            df_WRAT =  process_WRAT(args.input_dir + filename)
            # pp.pprint(df_hvlt.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
        elif (scale == 'NEO_FFI'):
            print("Processing Neo Five Factor Inventory Personality Test")
            df_WRAT =  process_NEO_FFI(args.input_dir + filename)
            # pp.pprint(df_hvlt.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))

    df_all_vars = df_CNC

    df_all_vars = df_all_vars.merge(df_AzBio, how="outer", on = ['SubjectNum', 'VisitDate'])
    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))

    df_all_vars = df_all_vars.merge(df_BAI, how="outer", on = ['SubjectNum', 'VisitDate'])

    df_all_vars = df_all_vars.merge(df_BDI, how="outer", on = ['SubjectNum', 'VisitDate'])

    df_all_vars = df_all_vars.merge(df_BVMT, how="outer", on = ['SubjectNum', 'VisitDate'])

    df_all_vars = df_all_vars.merge(df_HVLT, how="outer", on = ['SubjectNum', 'VisitDate'])

    df_all_vars = df_all_vars.merge(df_Trails, how="outer", on = ['SubjectNum', 'VisitDate'])

    df_all_vars = df_all_vars.merge(df_WAIS, how="outer", on = ['SubjectNum', 'VisitDate'])

    df_all_vars = df_all_vars.merge(df_WRAT, how="outer", on = ['SubjectNum', 'VisitDate'])

    df_all_vars = df_all_vars.merge(df_NEO_FFI, how="outer", on = ['SubjectNum', 'VisitDate'])

    pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitDate']))

    # Get the unique visits for all the subjects and calculate visit number
    df_unique_sub_visits = df_all_vars.sort_values(['SubjectNum', 'VisitDate']).groupby(['SubjectNum']).last().reset_index().loc[:, ["SubjectNum", "VisitDate"]]
    df_unique_sub_visits = df_unique_sub_visits.sort_values(['SubjectNum', 'VisitDate'])
    df_unique_sub_visits['VisitNum'] = df_unique_sub_visits.groupby(['SubjectNum']).cumcount()+1
    df_unique_sub_visits['VisitCode'] = df_unique_sub_visits['VisitNum']

    df_all_vars = df_all_vars.merge(df_unique_sub_visits, how="inner", on = ['SubjectNum', 'VisitDate'])
    # pp.pprint(df_all_vars)

    # Some times there seem to be multiple rows for the same event with different date. In such situations we are
    # arbitrarily deciding to use the last one that appears
    df_all_vars = df_all_vars.groupby(['SubjectNum', 'VisitCode']).last().reset_index()
    df_all_vars_sorted = df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate'])

    # Convert the wide format to long format to calculate the summary values such as change and rate of change
    df_all_vars_long = pd.melt(df_all_vars, id_vars=['SubjectNum', 'VisitCode', 'VisitDate', 'VisitNum'], var_name='Testname', value_name='Value')
    df_all_vars_long_sorted = df_all_vars_long.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate'])
    df_all_vars_long_sorted = df_all_vars_long_sorted.dropna()
    print("All observations:")
    pp.pprint(df_all_vars_long_sorted)

    # To calculate the difference and rate of change group by the patient and test and sort by VisitDate
    df_grouped_tests = df_all_vars_long_sorted.groupby(['SubjectNum', 'Testname']).nth([0, -1]).reset_index()
    df_grouped_tests = df_grouped_tests.sort_values(by = ['SubjectNum', 'Testname', 'VisitDate'])
    df_grouped_tests = df_grouped_tests.dropna()
    # pp.pprint(df_grouped_tests)

    print("Generating summary information")
    df_groups_with_multiple = df_all_vars_long_sorted.groupby(['SubjectNum', 'Testname']).filter(lambda x: len(x) > 1)
    pp.pprint(df_groups_with_multiple)
    # Filter out categorical variables from observations
    cat_vars_list = ["ESS_State", "REM_RBD_State", "GDS"]
    df_groups_with_multiple = df_groups_with_multiple[~df_groups_with_multiple.Testname.isin(cat_vars_list)]
    df_grouped_tests_summary = df_groups_with_multiple.groupby(['SubjectNum', 'Testname']).apply(calc_duration_change).reset_index()
    df_grouped_tests_summary = pd.melt(df_grouped_tests_summary.loc[:, ['SubjectNum', 'Testname', 'Change', 'ROC']], 
                                        id_vars=['SubjectNum', 'Testname'], var_name='Type', value_name="Value")
    df_grouped_tests_summary['Testname'] = df_grouped_tests_summary['Testname'] + "-" + df_grouped_tests_summary['Type']
    df_grouped_tests_summary = df_grouped_tests_summary.loc[:, ['SubjectNum', 'Testname', 'Value']] 
    print("Grouped test summary:")
    pp.pprint(df_grouped_tests_summary)

    print("Merged observations:")
    pp.pprint(df_all_obs)

    # Once the dataframes are created write the table to a CSV file
    # pp.pprint(df_pilot_bio.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))

    # pp.pprint(df_all_vars.sort_values(by = ['SubjectNum', 'VisitCode', 'VisitDate']))
    filename = "UI_CI_obs.csv"
    df_all_vars_sorted.to_csv(args.output_dir + filename, index = False)

    # pp.pprint(df_demo.sort_values(by = ['SubjectNum', 'Study']))
    filename = "UI_CI_demographics.csv"
    df_demo.to_csv(args.output_dir + filename, index = False)

    # pp.pprint(df_demo_long)
    filename = "UI_CI_demographics_long.csv"
    df_demo_long.to_csv(args.output_dir + filename, index = False)

    # pp.pprint(df_all_vars_long_sorted)
    filename = "UI_CI_obs_long.csv"
    df_all_obs.to_csv(args.output_dir + filename, index = False)

    # pp.pprint(df_grouped_tests_summary)
    filename = "UI_CI_obs_summary.csv"
    df_grouped_tests_summary.to_csv(args.output_dir + filename, index = False)

    # Before printing the subject visits calculate the age at visit
    df_unique_sub_visits = df_unique_sub_visits.merge(df_demo.loc[:, ['SubjectNum', 'Birthdate']], how="inner", on = ['SubjectNum'])
    df_unique_sub_visits['AgeAtVisit'] = df_unique_sub_visits["AgeAtNow"]
    df_unique_sub_visits['AgeAtVisit'] = df_unique_sub_visits
    # pp.pprint(df_unique_sub_visits)
    
    # Print a table of visit information
    filename = "UI_CI_visit_info.csv"
    df_unique_sub_visits.to_csv(args.output_dir + filename, index = False)

    # Print a table of unique tests in the data by combining the tests in the summary as well as observation
    # data frames
    unique_obs = df_all_obs.Testname.unique()
    unique_summary_obs = df_grouped_tests_summary.Testname.unique()
    unique_all_obs = np.concatenate([unique_obs, unique_summary_obs])
    pp.pprint(unique_all_obs)
    # df_unique_obs = pd.DataFrame({"Observations": df_all_obs.Testname.unique()})
    df_unique_obs = pd.DataFrame({"Observations": unique_all_obs})
    pp.pprint(df_unique_obs)
    filename = "UI_CI_unique_obs.csv"
    df_unique_obs.to_csv(args.output_dir + filename, index = False)

    # Print a table of unique subject variables in the data
    df_unique_subject_vars = pd.DataFrame({"Observations": df_demo_long.SubjectVar.unique()})
    # pp.pprint(df_unique_subject_vars)
    filename = "UI_CI_unique_subject_vars.csv"
    df_unique_subject_vars.to_csv(args.output_dir + filename, index = False)

if __name__ == '__main__':
    main()
