#!/usr/bin/env python3

"""
Load CI sample data into CliO-Vis database.
"""

import argparse
import csv
import mysql.connector
import re
import sys

# global vars
cliovis_db = 'cliovis'
user_id = 1             # admin user

# project
project_name = "Cochlear Implant Database"
project_descr = "Sample data from the Cochlear Implant database."
project_url = ""
project_is_public = 0

# study
study_name = "Combined/Hybrid CNC dataset"
study_descr = "Pre-op, 3, 6, 12 month CNC data in the combined and hybrid conditions for the Hybrid patients over time."

def main():
    parser = argparse.ArgumentParser( description='Load CI sample data into CliO-Vis database.')
    parser.add_argument('-s', '--static_file', type=str, required=True, help='Path to the "static" data file' )
    parser.add_argument('-i', '--implant_file', type=str, required=True, help='Path to the "implant" data file' )
    parser.add_argument('-c', '--cnc_file', type=str, required=True, help='Path to the "cnc" data file' )
    parser.add_argument('--host', type=str, required=False, default="127.0.0.1", help='MySQL server hostname' )
    parser.add_argument('-u', '--user', type=str, required=True, help='MySQL user name' )
    parser.add_argument('-p', '--password', type=str, required=True, help='MySQL password' )
    args = parser.parse_args()

    # connect to db
    try:
        conn = mysql.connector.connect(user=args.user, password=args.password, host=args.host, db=cliovis_db)
        cursor = conn.cursor()
    except Exception as e:
        print(e)
        sys.exit()
    print("Connected to MySQL server at " + args.host)
        
    # insert project and study
    project_id = get_or_insert_project(cursor, project_name, project_descr, user_id, project_url, project_is_public)
    print("Got project_id " + str(project_id))
    conn.commit()    

    study_id = get_or_insert_study(cursor, project_id, study_name, study_descr)
    print("Got study_id " + str(study_id))
    conn.commit()

    # retrieve subject_ontology and observation_ontology
    subject_ont = get_subject_ontology_index(cursor)
    observation_ont = get_observation_ontology_index(cursor)
    
    # insert subjects using data in static file
    n_subjects = 0
    n_atts = 0
    static_cols = []
    lnum = 0
    # track subjects by id
    subjects = {}

    # insert new ontology terms
    e1_id = insert_ontology_term(cursor, "subject", subject_ont, "Education (Years)", "Demographics")
    e1_id = insert_ontology_term(cursor, "subject", subject_ont, "Marital Status", "Demographics")
    e1_id = insert_ontology_term(cursor, "subject", subject_ont, "Native Language", "Demographics")
    e1_id = insert_ontology_term(cursor, "subject", subject_ont, "Retired", "Demographics")

    # created selected subject_ontology terms for implant data
    ci_id = insert_ontology_term(cursor, "subject", subject_ont, "Cochlear Implant", None)
    e1_id = insert_ontology_term(cursor, "subject", subject_ont, "Ear1", "Cochlear Implant")
    e2_id = insert_ontology_term(cursor, "subject", subject_ont, "Ear2", "Cochlear Implant")
    s1_id = insert_ontology_term(cursor, "subject", subject_ont, "Surgeon1", "Cochlear Implant")
    s2_id = insert_ontology_term(cursor, "subject", subject_ont, "Surgeon2", "Cochlear Implant")
    s1_id = insert_ontology_term(cursor, "subject", subject_ont, "Type1", "Cochlear Implant")
    s2_id = insert_ontology_term(cursor, "subject", subject_ont, "Type2", "Cochlear Implant")
    i1_id = insert_ontology_term(cursor, "subject", subject_ont, "Implant1 Age", "Cochlear Implant")
    i2_id = insert_ontology_term(cursor, "subject", subject_ont, "Implant2 Age", "Cochlear Implant")
    l1_id = insert_ontology_term(cursor, "subject", subject_ont, "lCauseLoss", "Cochlear Implant")
    l2_id = insert_ontology_term(cursor, "subject", subject_ont, "rCauseLoss", "Cochlear Implant")
    f_id = insert_ontology_term(cursor, "subject", subject_ont, "Device Failed", "Cochlear Implant")
    conn.commit()
    
    with open(args.static_file, newline='', encoding='ISO-8859-1') as sfile:
        reader = csv.reader(sfile, delimiter=',')
        for row in reader:
            lnum += 1
            
            hosp_id = row[0]
            # read column headers
            if re.match(r'.*HospitalNo.*', hosp_id):
                static_cols = row
            elif hosp_id != "":
                subject_id = get_or_insert_subject(cursor, study_id, hosp_id)
                conn.commit()
                n_subjects += 1

                # parse column data
                info = {}
                colnum = 0
                for col in static_cols:
                    if row[colnum] != "":
                        info[col] = row[colnum]
                    colnum += 1
                subjects[hosp_id] = info
                    
                # gender
                gender = 'unknown'
                if 'gender' in info:
                    gender = info['gender']
                    if gender == 'F':
                        gender = 'female'
                    elif gender == 'M':
                        gender = 'male'
                    else:
                        sys.stderr.write("unknown gender " + gender + " for subject " + hosp_id)
                        sys.exit(1)

                # race
                race = 'unknown'
                if 'race' in info and re.match(r'.*\S.*', info['race']):
                    race = info['race']

                # birthdate, age at first visit
                birthdate = info['birthdate']
                testdate = ""
                if 'testdate' in info:
                    testdate = info['testdate']

                # TODO - use "testdate" to compute age at first visit, otherwise use 2019
                # assume all birthdates are < 2000 and all first visit dates are >= 2000
                m1 = re.match(r'\d+\/\d+\/(\d+)', birthdate)
                birth_yr = 1900 + int(m1.group(1))

                first_visit_yr = None
                m2 = re.match(r'\d+\/\d+\/(\d+)', testdate)
                if m2 is not None:
                    first_visit_yr = 2000 + int(m2.group(1))
                else:
                    first_visit_yr = 2019

                # approximate first visit age
                first_visit_age = first_visit_yr - birth_yr

                # Education (Years)
                edu_years = 0
                if 'eduYears' in info and info['eduYears'] != "":
                    edu_years = info['eduYears']

                # Marital Status
                marital_status = "unknown"
                if 'maritalStatus' in info and info['maritalStatus'] != "":
                    marital_status = info['maritalStatus']

                # Native language
                native_lang = "unknown"
                if 'nativeLang' in info and info['nativeLang'] != "":
                    native_lang = info['nativeLang']

                # Retired
                retired = "unknown"
                if 'retired' in info and info['retired'] != "":
                    retired = info['retired']

                # lCauseLoss
                l_cause_loss = "unknown"
                if 'lCauseLoss' in info and info['lCauseLoss'] != "":
                    l_cause_loss = info['lCauseLoss']

                # rCauseLoss
                r_cause_loss = "unknown"
                if 'rCauseLoss' in info and info['rCauseLoss'] != "":
                    r_cause_loss = info['rCauseLoss']
                    
                # insert subject attributes
                insert_subject_attribute(cursor, subject_id, subject_ont, "Sex", gender, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Race", race, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Birthdate", birthdate, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Age at First Visit", first_visit_age, "int")

                insert_subject_attribute(cursor, subject_id, subject_ont, "Education (Years)", edu_years, "int")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Marital Status", marital_status, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Native Language", native_lang, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Retired", retired, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "lCauseLoss", l_cause_loss, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "rCauseLoss", r_cause_loss, "string")
                conn.commit()
                n_atts += 4

    print("inserted " + str(n_subjects) + " subject(s), " + str(n_atts) + " attribute(s)")

    # add implant info
    implant_cols = None
    with open(args.implant_file, newline='') as ifile:
        reader = csv.reader(ifile, delimiter=',')
        for row in reader:
            hosp_id = row[0]
            # read column headers
            if re.match(r'.*HospitalNo.*', hosp_id):
                implant_cols = row
            elif hosp_id != "":
                if hosp_id not in subjects:
                    print("implant file/skipping subject " + hosp_id + " not defined in static file")
                    continue
                
                info = {}
                colnum = 0
                for col in implant_cols:
                    if row[colnum] != "":
                        info[col] = row[colnum]
                    colnum += 1

                # insert selected data:
                # imp_age_mo, imp_age_yr
                # imp2_age_mo, imp2_age_yr
                # ear1
                # ear2
                # surgeon1
                # surgeon2
                # opdate1
                # opdate2
                #
                # device_failed
                #   based on comment1: device failed, explanted?
                #

                # set default values
                if 'ear1' not in info:
                    info['ear1'] = "N/A"
                if 'ear2' not in info:
                    info['ear2'] = "N/A"

                if 'surgeon1' not in info:
                    info['surgeon1'] = "N/A"
                if 'surgeon2' not in info:
                    info['surgeon2'] = "N/A"

                # implant age is in months if < 18 years old
                if 'imp_age_mo' in info and 'imp_age_yr' not in info:
                    info['imp_age_yr'] = int(float(info['imp_age_mo'])/12.0)
                if 'imp2_age_mo' in info and 'imp2_age_yr' not in info:
                    info['imp2_age_yr'] = int(float(info['imp2_age_mo'])/12.0)
                    
                dev_failed = "no"
                if 'comment1' in info and (re.match(r'.*(device failed|failed device).*', info['comment1'])):
                    dev_failed = "yes"

                if 'Type1' not in info:
                    info['Type1'] = 'N/A'
                if 'Type2' not in info:
                    info['Type2'] = 'N/A'

                subject_id = get_or_insert_subject(cursor, study_id, hosp_id)
                print("inserting additional attributes for " + str(subject_id))
                insert_subject_attribute(cursor, subject_id, subject_ont, "Ear1", info['ear1'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Ear2", info['ear2'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Surgeon1", info['surgeon1'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Surgeon2", info['surgeon2'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Type1", info['Type1'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Type2", info['Type2'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Device Failed", dev_failed, "string")

                # HACK - CliO-Vis expects all subject vars to be defined
                if 'imp_age_yr' in info:
                    insert_subject_attribute(cursor, subject_id, subject_ont, "Implant1 Age", info['imp_age_yr'], "int")
                else:
                    insert_subject_attribute(cursor, subject_id, subject_ont, "Implant1 Age", 0, "int")
                if 'imp2_age_yr' in info:
                    insert_subject_attribute(cursor, subject_id, subject_ont, "Implant2 Age", info['imp2_age_yr'], "int")
                else:
                    insert_subject_attribute(cursor, subject_id, subject_ont, "Implant2 Age", 0, "int")

                conn.commit()

    # created selected observation_ontology terms for CNC test results
    a_id = insert_ontology_term(cursor, "observation", observation_ont, "Aural", "Outcome Measures")
    a_terms = [
        "CombinedWord","HybridWord","IpsiHAWord_Pre","BilateralHAWord_Pre","ContraHA_Word_Pre"
    ]
    for term in a_terms:
        tid = insert_ontology_term(cursor, "observation", observation_ont, term, "Aural")

    # add visits and audiology results from
    # Maryland consonant-vowel nucleus-consonant (CNC) Tests
    visit_counts = {}
    cnc_cols = None
    # track last visit date for each subject
    subject_last_visit = {}

    with open(args.cnc_file, newline='') as cfile:
        reader = csv.reader(cfile, delimiter=',')
        for row in reader:
            hosp_id = row[0]
            # read column headers
            if re.match(r'.*HospitalNo.*', hosp_id):
                cnc_cols = row
            elif hosp_id != "":
                if hosp_id not in subjects:
                    print("cnc file/skipping subject " + hosp_id + " not defined in static file")
                    continue
                
                info = {}
                colnum = 0
                for col in cnc_cols:
                    if row[colnum] != "":
                        info[col] = row[colnum]
                    colnum += 1

                # HACK - ignore pre-op measurements
                if 'CombinedWord' not in info:
                    continue
                
#                print("read " + str(info))
                    
                # get subject id
                subject_id = get_or_insert_subject(cursor, study_id, hosp_id)

                # create subject_visit
                visit_num = 1
                if subject_id in visit_counts:
                    visit_num = visit_counts[subject_id] + 1
                visit_counts[subject_id] = visit_num
                disease_status = None

                # event date: convert m?m/dd/yy to yyyy-mm-dd
                event_date = info['testdate']
                m = re.match(r'^(\d+)\/(\d+)\/(\d{2})$', event_date)
                if m is not None:
                    event_date = '20' + m.group(3) + "-" + m.group(1).zfill(2) + "-" + m.group(2)

                visit_event = "Baseline"
                if visit_num > 1:
                    visit_event = "Visit " + str(visit_num)

                last_visit_date = None
                if subject_id in subject_last_visit:
                    last_visit_date = subject_last_visit[subject_id]
                # HACK - skip duplicate visit dates
                if last_visit_date == event_date:
                    print("skipping duplicate visit date for " + str(hosp_id))
                else:
                    subject_visit_id = get_or_insert_subject_visit(cursor, visit_event, visit_num, disease_status, event_date, subject_id)
                    conn.commit()

                    for term in a_terms:
                        if term in info:
                            obs_id = get_or_insert_observation(cursor, observation_ont, term, int(float(info[term])), subject_visit_id, "int")
                    conn.commit()

                subject_last_visit[subject_id] = event_date
                
    cursor.close()
    conn.close()

# Retrieve id of a project if it exists
def get_project_id(cursor, name, user_id):
    project_id = None
    query = "select id from project where project_name = %s and user_id = %s";
    try:
        cursor.execute(query, (name, user_id))
        for id in cursor:
            project_id = id[0]
    except Exception as e:
        print(e)
    return project_id
    
# Method that inserts a project in the database and returns the project ID
def get_or_insert_project(cursor, name, descr, user_id, url, is_public):
    project_id = get_project_id(cursor, name, user_id)
    if (project_id is not None):
        return project_id
    
    query = "insert into project (project_name, description, user_id, project_url, is_public) values (%s, %s, %s, %s, %s)";
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (name, descr, user_id, url, is_public))
        project_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created project '{}' in database with ID: {}.".format(project_name, project_id))
    return project_id

# Retrieve id of a study if it exists
def get_study_id(cursor, name, project_id):
    study_id = None
    query = "select id from study where study_name = %s and project_id = %s";
    try:
        cursor.execute(query, (name, project_id))
        for (id) in cursor:
            study_id = id[0]
    except Exception as e:
        print(e)
    return study_id

# Method that inserts the study in the database and returns the study ID
def get_or_insert_study(cursor, project_id, study_name, study_descr):
    study_id = get_study_id(cursor, study_name, project_id)
    if (study_id is not None):
        return study_id
    
    query = "insert into study (study_name, description, project_id) values (%s, %s, %s)"
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (study_name, study_descr, project_id))
        study_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created study entry '{}' in database with ID: {}.".format(study_name, study_id))
    return study_id

# Retrieve id of a subject if it exists
def get_subject_id(cursor, name, study_id):
    subject_id = None
    query = "select id from subject where subject_num = %s and study_id = %s";
    try:
        cursor.execute(query, (name, study_id))
        for (id) in cursor:
            subject_id = id[0]
    except Exception as e:
        print(e)
    return subject_id

# Method that inserts the subject in the database and returns the subject ID
def get_or_insert_subject(cursor, study_id, name):
    subject_id = get_subject_id(cursor, name, study_id)
    if (subject_id is not None):
        return subject_id
    
    query = "insert into subject (study_id, subject_num) values (%s, %s)"
    try:
        cursor.execute(query, (study_id, name))
        subject_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject entry '{}' in database with ID: {}.".format(name, subject_id))
    return subject_id

def get_subject_ontology_index(cursor):
    idx = dict()
    query = "SELECT id, label, parent_id FROM subject_ontology"
    try:
        cursor.execute(query)
        for row in cursor:
            idx[row[1]] = {'id': row[0], 'parent_id': row[2]}

    except Exception as e:
        print(e)
        sys.exit()

    return idx

def get_observation_ontology_index(cursor):
    idx = dict()
    query = 'SELECT id, label, parent_id FROM observation_ontology'
    try:
        cursor.execute(query)
        for row in cursor:
            idx[row[1]] = dict(id=row[0], parent_id=row[2])
    except Exception as e:
        print(e)
        sys.exit()

    return idx

def get_subject_attribute_id(cursor, subject_id, subject_ont_id):
    subj_att_id = None
    query = "select id from subject_attribute where subject_id = %s and subject_ontology_id = %s"
    try:
        cursor.execute(query, (subject_id, subject_ont_id))
        for (id) in cursor:
            subj_att_id = id[0]
    except Exception as e:
        print(e)
    return subj_att_id

def insert_subject_attribute(cursor, subject_id, subject_ont, term, value, type):
    if term not in subject_ont:
        print("ERROR - no subject_ontology term found for '" + term+ "'")
        sys.exit(1)

    ont_id = subject_ont[term]['id']

    # don't insert a duplicate (or try to update an existing value)
    attribute_id = get_subject_attribute_id(cursor, subject_id, ont_id)
    if (attribute_id is not None):
        return attribute_id

    query = "insert into subject_attribute (subject_id, subject_ontology_id, value, value_type) values (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (subject_id, ont_id, value, type))
        attribute_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    return attribute_id

def insert_ontology_term(cursor, ontology, ontology_index, label, parent_term):
    parent_id = None

    if (parent_term is not None):
        if parent_term not in ontology_index:
            print("ERROR - no " + ontology + "_ontology term found for '" + parent_term + "'")
            sys.exit(1)
        parent_id = ontology_index[parent_term]['id']

    # don't insert a duplicate (or try to update an existing value)
    if label in ontology_index:
        return ontology_index[label]['id']

    query = "insert into " + ontology + "_ontology (label, parent_id) values (%s, %s)"
    try:
        cursor.execute(query, (label, parent_id))
        ontology_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    # update index
    ontology_index[label] = { 'id': ontology_id, 'label': label, 'parent_id': parent_id }
    return ontology_id

def get_subject_visit_id(cursor, visit_num, subject_id):
    subject_visit_id = None
    query = "select id from subject_visit where visit_num = %s and subject_id = %s";
    try:
        cursor.execute(query, (visit_num, subject_id))
        for (id) in cursor:
            subject_visit_id = id[0]
    except Exception as e:
        print(e)
    return subject_visit_id

def get_or_insert_subject_visit(cursor, visit_event, visit_num, disease_status, event_date, subject_id):
    subject_visit_id = get_subject_visit_id(cursor, visit_num, subject_id)
    if (subject_visit_id is not None):
        return subject_visit_id
    
    query = "insert into subject_visit (visit_event, visit_num, disease_status, event_date, subject_id) values (%s, %s, %s, %s, %s)"
    try:
        cursor.execute(query, (visit_event, visit_num, disease_status, event_date, subject_id))
        subject_visit_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject visit {}/{} in database with ID: {}.".format(str(subject_id), str(visit_num), subject_visit_id))
    return subject_visit_id

def get_observation_id(cursor, subject_visit_id, obs_ont_id):
    obs_id = None
    query = "select id from observation where subject_visit_id = %s and observation_ontology_id = %s"
    try:
        cursor.execute(query, (subject_visit_id, obs_ont_id))
        for (id) in cursor:
            obs_id = id[0]
    except Exception as e:
        print(e)
    return obs_id

def get_or_insert_observation(cursor, observation_ont, term, value, subject_visit_id, type):
    if term not in observation_ont:
        print("ERROR - no observation_ontology term found for '" + term+ "'")
        sys.exit(1)

    ont_id = observation_ont[term]['id']

    # don't insert a duplicate (or try to update an existing value)
    obs_id = get_observation_id(cursor, subject_visit_id, ont_id)
    if (obs_id is not None):
        return obs_id

    query = "insert into observation (observation_ontology_id, value, subject_visit_id, value_type) values (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (ont_id, value, subject_visit_id, type))
        obs_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    return obs_id

if __name__ == '__main__':
    main()
