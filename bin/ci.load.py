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
study_name = "Cochlear Implant sample data"
study_descr = "Cochlear Implant data from sample spreadsheet."


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
    with open(args.static_file, newline='') as sfile:
        reader = csv.reader(sfile, delimiter=',')
        for row in reader:
            # ac = A/C (Adult/Child)
            # gender = M/F
            (hosp_id, check_digit, birthday, age_mo, age_yr, ac, gender, deceased, sched_comments, comments) = row

            # skip headers
            if hosp_id != "" and not re.match(r'.*hosp_no.*', hosp_id):
                subject_id = get_or_insert_subject(cursor, study_id, hosp_id)
                conn.commit()
                n_subjects += 1
                
                # gender
                if gender == 'F':
                    gender = 'female'
                elif gender == 'M':
                    gender = 'male'

                # age - months used for < 18 years old
                if age_mo != "" and age_yr == "":
                    age_yr = int(float(age_mo) / 12.00)

                # age - CliO-Vis can't handle empty values here
                if age_yr == "":
                    age_yr = 200

                # insert subject attributes
                insert_subject_attribute(cursor, subject_id, subject_ont, "Sex", gender, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Race", "unknown", "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Birthdate", birthday, "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Age at First Visit", age_yr, "int")
                conn.commit()
                n_atts += 4

    print("inserted " + str(n_subjects) + " subject(s), " + str(n_atts) + " attribute(s)")

    implant_cols = ['hosp_id','SID','grant_yn','withdrawdate','withdrawreason','ear1','ear2','ear3','Laby1','Laby2','Laby3','DeceasedYN','Code1_1','Code1_2','Code2_1','Code2_2','Code3_1','Code3_2','typ1','typ1extra','typ2','typ2extra','typ3','typ3extra','ser1','ser1extra','ser2','ser2extra','ser3','ser3extra','UIHC1','UIHC2','UIHC3','opdate1','opdate2','opdate3','condate1','condate2','condate3','new_typi','new_typ1','new_typ2','new_typ3','cur_typ1','cur_typ2','cur_typ3','updatei','update1','update2','update3','inactdatei','inactdate1','inactdate2','inactdate3','nele1','nele2','nele3','status_speech','status_audio','status_ep','status_music','imp_age_yr','imp_age_mo','imp2_age_yr','imp2_age_mo','imp_comment','consentdate','assentdate','surgeon1','surgeon2','surgeon3','comment1','comment2','comment3','grantator_yn','evergrant_yn','whynotstudy','when_nu_or_do','active','annual_recall','longterm_yn','entrydate']

    # created selected subject_ontology terms for implant data
    ci_id = insert_ontology_term(cursor, "subject", subject_ont, "Cochlear Implant", None)
    e1_id = insert_ontology_term(cursor, "subject", subject_ont, "Ear1", "Cochlear Implant")
    e2_id = insert_ontology_term(cursor, "subject", subject_ont, "Ear2", "Cochlear Implant")
    s1_id = insert_ontology_term(cursor, "subject", subject_ont, "Surgeon1", "Cochlear Implant")
    s2_id = insert_ontology_term(cursor, "subject", subject_ont, "Surgeon2", "Cochlear Implant")
    i1_id = insert_ontology_term(cursor, "subject", subject_ont, "Implant1 Age", "Cochlear Implant")
    i2_id = insert_ontology_term(cursor, "subject", subject_ont, "Implant2 Age", "Cochlear Implant")
    f_id = insert_ontology_term(cursor, "subject", subject_ont, "Device Failed", "Cochlear Implant")
    conn.commit()

    # add implant info
    with open(args.implant_file, newline='') as ifile:
        reader = csv.reader(ifile, delimiter=',')
        for row in reader:
            hosp_id = row[0]
            # skip headers
            if hosp_id != "" and not re.match(r'.*hosp_no.*', hosp_id):
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
                    
#                print("read " + str(info))

                subject_id = get_or_insert_subject(cursor, study_id, hosp_id)
                print("inserting additional attributes for " + str(subject_id))
                insert_subject_attribute(cursor, subject_id, subject_ont, "Ear1", info['ear1'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Ear2", info['ear2'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Surgeon1", info['surgeon1'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Surgeon2", info['surgeon2'], "string")
                insert_subject_attribute(cursor, subject_id, subject_ont, "Device Failed", dev_failed, "string")

                if 'imp_age_yr' in info:
                    insert_subject_attribute(cursor, subject_id, subject_ont, "Implant1 Age", info['imp_age_yr'], "int")
                if 'imp2_age_yr' in info:
                    insert_subject_attribute(cursor, subject_id, subject_ont, "Implant2 Age", info['imp2_age_yr'], "int")

                conn.commit()

    # created selected observation_ontology terms
#    ci_id = insert_ontology_term(cursor, "subject", subject_ont, "Cochlear Implant", None)

#    conn.commit()
                
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
    
if __name__ == '__main__':
    main()
