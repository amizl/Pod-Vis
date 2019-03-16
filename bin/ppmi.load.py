#!/usr/bin/env python3

"""

Put some general, high-level documentation here

"""

import argparse
import re
import sys
import mysql.connector
from mysql.connector import Error

study_map = {}
patient_map = {}
project_id = 1

def main():
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_file', type=str, required=True, help='Path to an input file to be read' )
    args = parser.parse_args()

    # Establish a connection the database
    try:
        conn = mysql.connector.connect(user='testuser', password='test@1940!',
                                       host='127.0.0.1',
                                       db='cliovis')
        cursor = conn.cursor()
        
        if conn.is_connected():
            print('Connected to MySQL database')

    except Error as e:
        print(e)
        sys.exit()

    # Open the file an iterate over the list
    with open(args.input_file) as ifh:
        line = ifh.readline() # Ignore header line

        # Process the remaining lines
        for line in ifh:
            line = line.rstrip()
            subject_num, sex, study_group, race, birth_date, gene_category, disease_status, event_date, score, scale, event, item, category = re.split("\t", line)

            # event values are: 

            print("Patient ID: {} event date {} measure {} value {}".format(subject_num, event_date, item, score))

            # Check to see if an entry for this study already exists, if not create one
            study_id = 0
            if (study_group not in study_map):
                study_id = get_study_entry(cursor, study_group, project_id)
                if (study_id == 0):
                    # As the study ID does not exist in the database create it
                    study_id = create_study_entry(cursor, study_group, project_id)
                    conn.commit()

                study_map[study_group] = study_id
            else:
                study_id = study_map[study_group]

            # Check to see if this subject already exists in database, if so use the ID
            # else create an entry
            subject_id = 0
            if (subject_num not in patient_map):
                subject_id = get_subject_entry(cursor, subject_num, study_id)
                if (subject_id == 0):
                    # As the subject entry does not exist in database create it
                    subject_id = create_subject_entry(cursor, subject_num, study_id, birth_date, sex, race)
                    conn.commit()

                patient_map[subject_num] = {'subject_id' : subject_id}
            else:
                subject_id = patient_map[subject_num]['subject_id']

            subject_info = patient_map[subject_num]
            
            # If no visits have been processed yet then create a map to hold visits
            if ('visits' not in subject_info):
                subject_info['visits'] = {}
            subject_visits = subject_info['visits']

            # Check to see if this subject visit already exists in database, if so use the ID
            # else create an entry
            subject_visit_id = 0
            if (visit_num not in subject_visits):
                subject_visit_id = get_subject_visit(cursor, visit_num, subject_id)
                if (subject_visit_id == 0):
                    # As the subject visit entry does not exist in database create it
                    subject_visit_id = create_subject_visit(cursor, visit_num, subject_id, event, event_date, disease_status)
                    patient_map[subject_num]['visits'][visit_num] = subject_visit_id
                    conn.commit()
            else:
                subject_visit_id = subject_visits[visit_num]

            # Check to see if this observation exists, if not add it to the database
            observation_id = get_subject_observation(cursor, subject_visit_id, item)
            if (observation_id == 0):
                # AS this observation does not exist in the table, create it
                observation_id = create_subject_observation(cursor, subject_visit_id, item, score, category, scale)
                conn.commit()

            

# Method that inserts the study in the database and returns the study ID
def create_study_entry(cursor, study_name, project_id):
    study_id = 0
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)
        study_id = cursor.lastrowid
 
    except Error as e:
        print(e)
        sys.exit()

    print("Created study entry '{}' in database with ID: {}.".format(study_name, study_id))
    return study_id

# Method that inserts the subject in the database and returns the subject ID
def create_subject_entry(cursor, subject_num, study_id, birth_date, sex, race):
    subject_id = 0
    query = "insert into subject (subject_num, study_id) values ('{}', {})".format(subject_num, study_id)
    try:
        cursor.execute(query)
        subject_id = cursor.lastrowid
 
    except Error as e:
        print(e)
        sys.exit()

    print("Created subject entry '{}' in database with ID: {}.".format(subject_num, study_id))
    return subject_id

# Method that inserts the observation in the database and returns the observation ID
def create_subject_observation(subject_visit_id, item, score, category, scale):
    observation_id = 0
    query = "insert into observations (subject_visit_id, item, value, category, scale) values ({}, '{}', {}, '{}', '{}')".format(subject_visit_id, item, score, category, scale)
    try:
        cursor.execute(query)
        observation_id = cursor.lastrowid
 
    except Error as e:
        print(e)
        sys.exit()

    print("Created subject observation '{}' in database with subject visit ID: {}.".format(item, subject_visit_id))
    return observation_id

# Method that inserts the visit in the database and returns the visit ID
def create_subject_visit(cursor, visit_num, subject_id, visit_event, event_date, disease_status):
    visit_id = 0
    query = "insert into subject_visit (visit_num, subject_id, visit_event, event_date, disease_status) values ({}, {}, '{}', '{}', '{}')".format(visit_num, subject_id, visit_event, event_date, disease_status)
    try:
        cursor.execute(query)
        visit_id = cursor.lastrowid
 
    except Error as e:
        print(e)
        sys.exit()

    print("Created subject visit '{}' in database with subject ID: {}.".format(visit_num, subject_id))
    return visit_id

# Method that checks for the observation in the database and returns the observation ID, else zero
def get_subject_observation(cursor, subject_visit_id, item):
    observation_id = 0
    # First check if this observation already exists in which case just read the observation ID and return it
    query = "SELECT id FROM observations where item = '{}' AND subject_visit_id = {}".format(item, subject_visit_id)
    try:
        cursor.execute(query)
 
        row = cursor.fetchone()
        if row is not None:
            observation_id = row[0]
    except Error as e:
        print(e)
        sys.exit()

    return observation_id


# Method that checks for the visit in the database and returns the visit ID, else zero
def get_subject_visit(cursor, visit_num, subject_id):
    visit_id = 0
    # First check if this visit already exists in which case just read the visit ID and return it
    query = "SELECT id FROM subject_visit where visit_num = '{}' AND subject_id = {}".format(visit_num, subject_id)
    try:
        cursor.execute(query)
 
        row = cursor.fetchone()
        if row is not None:
            visit_id = row[0]
    except Error as e:
        print(e)
        sys.exit()

    return visit_id

# Method that checks for the study in the database and returns the study ID, else zero
def get_study_entry(cursor, study_name, project_id):
    study_id = 0
    # First check if this entry already exists in which case just read the study ID and return it
    query = "SELECT id FROM study where study_name = '{}' AND project_id = {}".format(study_name.replace("'", "''"), project_id)
    try:
        cursor.execute(query)
 
        row = cursor.fetchone()
        if row is not None:
            study_id = row[0]
            
    except Error as e:
        print(e)
        sys.exit()

    return study_id

# Method that checks for the subject in the database and returns the subject ID, else zero
def get_subject_entry(cursor, subject_num, study_id):
    subject_id = 0
    # First check if this entry already exists in which case just read the subject ID and return it
    query = "SELECT id FROM subject where subject_num = '{}' AND study_id = {}".format(subject_num, study_id)
    try:
        cursor.execute(query)
 
        row = cursor.fetchone()
        if row is not None:
            subject_id = row[0]
            
    except Error as e:
        print(e)
        sys.exit()

    return subject_id




if __name__ == '__main__':
    main()



