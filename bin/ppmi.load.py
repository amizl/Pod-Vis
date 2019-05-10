#!/usr/bin/env python3

"""

Put some general, high-level documentation here

"""

import argparse
import re
import sys
import mysql.connector

study_map = {}
patient_map = {}
subject_attr_map = {}
project_id = 1

def main():
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_file', type=str, required=True, help='Path to an input file to be read' )
    parser.add_argument('-u', '--user', type=str, required=True, help='MySQL user name' )
    parser.add_argument('-p', '--password', type=str, required=True, help='MySQL password' )
    args = parser.parse_args()

    # Establish a connection the database
    try:
        conn = mysql.connector.connect(user=args.user, password=args.password,
                                       host='127.0.0.1',
                                       db='cliovis')
        cursor = conn.cursor()

        if conn.is_connected():
            print('Connected to MySQL database')

    except Exception as e:
        print(e)
        sys.exit()

    subject_ont = get_subject_ontology_index(cursor)
    observation_ont = get_observation_ontology_index(cursor)

    # Open the file an iterate over the list
    with open(args.input_file) as ifh:
        line = ifh.readline() # Ignore header line

        # Process the remaining lines
        for line in ifh:
            line = line.rstrip()
            # from ppmi_derived_visits.tsv
            subject_num, sex, study_group, race, birth_date, disease_status, event_date, score, scale, event, item, category, age, visit_num = re.split("\t", line)
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

            if 'Outcome Measures' not in observation_ont:
                add_observation_ontology_term(cursor, observation_ont, 'Outcome Measures', None)
            if category not in observation_ont:
                add_observation_ontology_term(cursor, observation_ont, category, observation_ont['Outcome Measures']['id'])
            if scale not in observation_ont:
                add_observation_ontology_term(cursor, observation_ont, scale, observation_ont[category]['id'])
            if item not in observation_ont:
                add_observation_ontology_term(cursor, observation_ont, item, observation_ont[scale]['id'])
            # Check to see if this observation exists, if not add it to the database
            observation_id = get_subject_observation(cursor, subject_visit_id, observation_ont[item]['id'])
            if (observation_id == 0):
                # AS this observation does not exist in the table, create it
                observation_ont_id = observation_ont[item]['id']
                observation_id = create_subject_observation(cursor, subject_visit_id, observation_ont_id, score)

            # columns with subject attributes (0-based)
            #  1:female(gender) 3:hispanic(race)
            for term in ['Sex', 'Race', 'Birthdate']:
                if term not in subject_ont:
                    add_subject_ontology_term(cursor, subject_ont, term)

            if subject_id not in subject_attr_map:
                add_subject_attribute(cursor, subject_id, subject_ont['Sex']['id'], sex, 'string')
                add_subject_attribute(cursor, subject_id, subject_ont['Race']['id'], race, 'string')
                add_subject_attribute(cursor, subject_id, subject_ont['Birthdate']['id'], birth_date, 'date')
                subject_attr_map[subject_id] = True

            conn.commit()


def add_subject_attribute(cursor, subject_id, ont_id, val, val_type):
    query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (subject_id, ont_id, val, val_type))

def add_subject_ontology_term(cursor, ont, term):
    query = "INSERT INTO subject_ontology (label) VALUES (%s)"
    cursor.execute(query, (term,))
    ont[term] = {'id': cursor.lastrowid, 'parent_id': None}

def add_observation_ontology_term(cursor, ont, term, parent_id=None):
    query = "INSERT INTO observation_ontology (label, parent_id) VALUES (%s, %s)"
    cursor.execute(query, (term, parent_id))
    ont[term] = {'id': cursor.lastrowid, 'parent_id': parent_id}

# Method that inserts the study in the database and returns the study ID
def create_study_entry(cursor, study_name, project_id):
    study_id = 0
    query = "insert into study (study_name, project_id) values ('{}', {})".format(study_name.replace("'", "''"), project_id)
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)
        study_id = cursor.lastrowid

    except Exception as e:
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

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject entry '{}' in database with ID: {}.".format(subject_num, study_id))
    return subject_id

# Method that inserts the observation in the database and returns the observation ID
def create_subject_observation(cursor, subject_visit_id, obs_ont_id, value):
    observation_id = 0
    query = "insert into observation (subject_visit_id, observation_ontology_id, value, value_type) values (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (subject_visit_id, obs_ont_id, value, 'int'))
        observation_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject observation '{}' in database with subject visit ID: {}.".format(obs_ont_id, subject_visit_id))
    return observation_id

# Method that inserts the visit in the database and returns the visit ID
def create_subject_visit(cursor, visit_num, subject_id, visit_event, event_date, disease_status):
    visit_id = 0
    query = "insert into subject_visit (visit_num, subject_id, visit_event, event_date, disease_status) values ({}, {}, '{}', '{}', '{}')".format(visit_num, subject_id, visit_event, event_date, disease_status)
    try:
        cursor.execute(query)
        visit_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject visit '{}' in database with subject ID: {}.".format(visit_num, subject_id))
    return visit_id

# Method that checks for the observation in the database and returns the observation ID, else zero
def get_subject_observation(cursor, subject_visit_id, obs_ont_id):
    observation_id = 0
    # First check if this observation already exists in which case just read the observation ID and return it
    query = "SELECT id FROM observation where observation_ontology_id = '{}' AND subject_visit_id = {}".format(obs_ont_id, subject_visit_id)
    try:
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            observation_id = row[0]
    except Exception as e:
        print(e)
        sys.exit()

    return observation_id


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
    except Exception as e:
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

    except Exception as e:
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

    except Exception as e:
        print(e)
        sys.exit()

    return subject_id




if __name__ == '__main__':
    main()
