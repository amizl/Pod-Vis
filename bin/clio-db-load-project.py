#!/usr/bin/env python3

"""
A script to load the project information in the cliovis database. The data is loaded from
a tab delimited file with the following header.

The data is loaded in two tables, the project table and the study table. If recordes exist they are
updated, if not new records are created.
"""

import argparse
import re
import sys
import csv
import mysql.connector
import pandas as pd
import pprint as pp
from decimal import *

study_map = {}
subject_map = {}
patient_map = {}
subject_attr_map = {}
project_map = {}
subject_ont = {}
observation_ont = {}
project_id = 1

def main():
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_file', type=str, required=True, help='Path to an input file that gives mapping between database modules and data files associated with module' )
    parser.add_argument('-d', '--input_dir', type=str, required=True, help='Path to directory where the input files are located' )
    parser.add_argument('-m', '--mapping_file', type=str, required=True, help='Path to the column names to field mapping file' )
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

    # Read the input file which gives the mapping between entities and the files with the data
    df_entity_file_map = pd.read_csv(args.input_file) 
    # pp.pprint(df_entity_file_map)

    # Read the input file which gives the mapping between column names and database field names
    df_col_names_field_map = pd.read_csv(args.mapping_file, index_col="Ontology Label") 
    pp.pprint(df_col_names_field_map)

    # Read the info from some of the tables as data frames
    df_project_info = get_project_info(conn)
    df_study_info = get_study_info(conn)
    # df_subject_ont_info = get_subject_ontology_info(conn)
    # df_observation_ont_info = get_observation_ontology_info(conn)

    # Load some of the info as dictionaries
    subject_ont = get_subject_ontology_index(cursor)
    observation_ont = get_observation_ontology_index(cursor)

    # pp.pprint(df_project_info)
    # pp.pprint(df_study_info)
    pp.pprint(subject_ont)
    # pp.pprint(observation_ont)

    # Loop through the entity_file_map and process each file
    # The order is important as processing project, subject ontology, and observation ontology 
    # before any other records are created is important
    entities = ["Project", "Subject Ontology", "Observation Ontology", "Subject Info", "Visit", "Observations", "Observations Summary"]
    for entity in entities:
        entity_file = df_entity_file_map.loc[df_entity_file_map['Entity'] == entity]['File'].item()
        pp.pprint(entity_file)
        entity_file = args.input_dir + entity_file
        print("Processing entity: %s file: %s" % (entity, entity_file))
        if entity is "Project":
            print("Processing project and studies .....")
            process_projects_and_studies(cursor, conn, entity_file, df_project_info, df_study_info, df_col_names_field_map)
        elif entity is "Subject Ontology":
            print("Processing subject ontology .....")
            process_subject_ontology(cursor, conn, entity_file, subject_ont, df_col_names_field_map)
        elif entity is "Observation Ontology":
            print("Processing observation ontology .....")
            process_observation_ontology(cursor, conn, entity_file, observation_ont, df_col_names_field_map)
        elif entity is "Subject Info":
            print("Processing subject information .....")
            process_subject_info(cursor, conn, entity_file, study_map, subject_ont, df_col_names_field_map)
        elif entity is "Visit":
            print("Processing visit information .....")
            process_subject_visits(cursor, conn, entity_file, df_col_names_field_map)

    exit()

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


# Process the subject visits file to create or update entries inthe subject_visit table
# tables. The file has the following columns:
# SubjectNum,VisitCode,VisitDate
def process_subject_visits(cursor, conn, visit_file, df_col_names_field_map):

    pp.pprint(subject_map)

    # Open the file an iterate over the list
    with open(visit_file) as ifh:

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            # from ppmi_projects.csv
            pp.pprint(row)
            subject_num = row['SubjectNum']
            visit_code = row['VisitCode']
            visit_date = row['VisitDate']
            visit_num = row['VisitNum']
            disease_status = row['VisitDiseaseStatus']

            if subject_num in subject_map:
                subject_info = subject_map[subject_num]
                subject_id = subject_info["id"]
            else:
                print("Cannot find subject num {} in subject map. Skipping entry .....".format(subject_num))

            print("Subject: {} ID: {} Visit Code: {} Visit Date: {} Visit Num: {}".format(subject_num, subject_id, visit_code, visit_date, visit_num))

            # If no visits have been processed yet then create a map to hold visits
            if ('visits' not in subject_info):
                subject_info['visits'] = {}
            subject_visits = subject_info['visits']

            # Check to see if this subject visit already exists in database, if so use the ID
            # else create an entry
            subject_visit_id = 0
            if (visit_num not in subject_visits):
                subject_visit_id = get_subject_visit(cursor, subject_id, visit_num)
                if (subject_visit_id == 0):
                    # As the subject visit entry does not exist in database create it
                    subject_visit_id = create_subject_visit(cursor, subject_id, visit_num, visit_code, 
                                                            visit_date, disease_status)
                    subject_map[subject_num]['visits'][visit_num] = subject_visit_id
                    conn.commit()
                else:
                    # Visit already exists, so update the visit
                    update_subject_visit(cursor, subject_visit_id, visit_code, visit_date, disease_status)
                    subject_map[subject_num]['visits'][visit_num] = subject_visit_id
                    conn.commit()
            else:
                subject_visit_id = subject_visits[visit_num]            


# Process the projects file and create missing entries or update existing entries in the 'project' and 'study'
# tables. The file has the following columns:
# project_name	project_description	primary_diease	study_name	longitudinal	study_description
def process_projects_and_studies(cursor, conn, project_file, df_project_info, df_study_info, df_col_names_field_map):

    # Open the file an iterate over the list
    with open(project_file) as ifh:
        # dialect = csv.Sniffer().sniff(ifh.read(1024))
        # ifh.seek(0)
        # next(ifh) # Skip the header line

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            # from ppmi_projects.csv
            pp.pprint(row)
            project_name = row['project_name']
            project_description = row['project_description']
            primary_disease = row['primary_diease']
            study_name = row['study_name']
            longitudinal = row['longitudinal']
            study_description = row['study_description'] 

            # project and study values are:
            print("Project: {}\nProject desc: {}\nPrimary Disease: {}\nStudy Name: {}\nStudy Description: {}\nLongitudinal: {}".format(project_name, project_description,
                                                                                                                                        primary_disease, study_name,
                                                                                                                                        study_description, longitudinal))

            # See if this project exists in the project map in which case update it, else create an entry
            project_id = 0
            if (project_name not in project_map):
                project_id = get_project_entry(cursor, project_name)
                if (project_id == 0):
                    # As the project ID does not exist create a project ID
                    project_id = create_project_entry(cursor, project_name, primary_disease, project_description)
                    conn.commit()
                else:
                    # As the project ID exists, update the project record
                    update_project_entry(cursor, project_id, project_name, primary_disease, project_description)
                    conn.commit()

                project_map[project_name] = project_id
            else:
                project_id = project_map[project_name]

            # Check to see if an entry for this study already exists, if not create one
            study_id = 0
            if (study_name not in study_map):
                study_id = get_study_entry(cursor, study_name, project_id)
                if (study_id == 0):
                    # As the study ID does not exist in the database create it
                    study_id = create_study_entry(cursor, study_name, longitudinal, study_description, project_id)
                    conn.commit()
                else:
                    # As the project ID exists, update the project record
                    update_study_entry(cursor, study_id, study_name, longitudinal, study_description, project_id)
                    conn.commit()

                study_map[study_name] = study_id
            else:
                study_id = study_map[study_name]

# Process the subject ontology file to create or update entries in the 'subject_ontology'
# table. The file has the following columns:
# Observations
def process_subject_ontology(cursor, conn, subject_ont_file, subject_ont, df_col_names_field_map):

    # Open the file an iterate over the list
    with open(subject_ont_file) as ifh:
        # dialect = csv.Sniffer().sniff(ifh.read(1024))
        # ifh.seek(0)
        # next(ifh) # Skip the header line

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            subject_var = row['Observations']
            print("Processing variable: {}".format(subject_var))

            # Look for this observation in the field map
            map_row = df_col_names_field_map.loc[subject_var]
            database_entity = map_row['Database Entity']
            value_type = map_row['Type']
            data_category = map_row['Data Type']
            category = map_row['Category']
            scale = str(map_row['Scale'])

            # Make sure that the variable belongs to the subject_ontology table, else skip
            # For instance the variable Study does not belong, so skip
            if (database_entity != "subject_ontology"):
                print("Variable {} is not in subject ontology, skipping ....".format(subject_var))
                continue

            subject_ont_id = 0
            category_id = 0
            scale_id = 0
            parent_id = 0

            # Check to see if the parent terms exist in the ontology map read from the 
            # database, if they do use the same IDs, else create them
            if (category not in subject_ont):
                print("Cannot find {} in subject ontology.".format(category))
                # As the category ID does not exist in the database create it
                category_id = create_subject_ontology_term(cursor, category)
                conn.commit()

                subject_ont[category] = {'id': category_id, 'parent_id': 0}
            else:
                category_id = subject_ont[category]['id']

            print("Category ID: {}".format(category_id))

            # Not every term has a scale, so check to see if the scale field is empty in 
            # which case use the category ID as the parent ID
            if scale == 'nan' or scale == 'NaN':
                parent_id = category_id
            else:
                # Check to see if the parent terms exist in the table, if not create them
                if (scale not in subject_ont):
                    print("Cannot find {} in subject ontology.".format(scale))
                    # As the scale ID does not exist in the database create it
                    scale_id = create_subject_ontology_term(cursor, scale, category_id)
                    conn.commit()

                    subject_ont[scale] = {'id': scale_id, 'parent_id': 0}
                else:
                    scale_id = subject_ont[scale]['id']
                
                # As the scale exists, set the parent ID to scale ID
                parent_id = scale_id

            # Check to see if the subject variable exists, if not create it    
            # If it does update it, else create a new entry
            subject_ont_id = get_subject_ontology(cursor, subject_var)
            print("Subject variable: {} ontology ID: {}\n".format(subject_var, subject_ont_id))
            if (subject_ont_id == 0):
                # As the subject_ont ID does not exist in the database create it
                subject_ont_id = create_subject_ontology_term(cursor, subject_var, parent_id, value_type, data_category)
                conn.commit()
                subject_ont[subject_var] = {'id': category_id, 'parent_id': parent_id}
            else:
                # As the ontology ID exists, update the ontology record
                update_subject_ontology_term(cursor, subject_ont_id, subject_var, parent_id, value_type, data_category) 
                conn.commit()


# Process the observation ontology file to create or update entries in the 'observation_ontology'
# table. The file has the following columns:
# Observations
def process_observation_ontology(cursor, conn, observation_ont_file, observation_ont, df_col_names_field_map):

    # Open the file an iterate over the list
    with open(observation_ont_file) as ifh:
        # dialect = csv.Sniffer().sniff(ifh.read(1024))
        # ifh.seek(0)
        # next(ifh) # Skip the header line

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            observation_var = row['Observations']
            print("Processing variable: {}".format(observation_var))

            # Look for this observation in the field map
            # Because an observation could have summary values we have to handle thos as well
            # For instance Semantic Fluency has observations, but may also have change and ROC
            # as additional observation summary values that need to be handled
            map_rows = df_col_names_field_map.loc[df_col_names_field_map['Testname'] == observation_var]
            pp.pprint(map_rows)
            for index, row in map_rows.iterrows():
                print(index, row['Entry Type'])
                database_entity = row['Database Entity']
                value_type = row['Type']
                data_category = row['Data Type']
                category = row['Category']
                scale = str(row['Scale'])
                flip_axis = row['Flip Axis']
                ordinal_sort = row['Ordinal Sort']
                entry_type = row['Entry Type']
                observation_term = index

                print("Processing observation term: {} flip axis: {}".format(observation_term, flip_axis))

                # Make sure that the variable belongs to the observation_ontology table, else skip
                # For instance the variable Study does not belong, so skip
                if (database_entity != "observation_ontology" and database_entity != "observation_summary"):
                    print("Variable {} is not in observation ontology or summary, skipping ....".format(observation_term))
                    continue

                observation_ont_id = 0
                category_id = 0
                scale_id = 0
                parent_id = 0

                # Check to see if the parent terms exist in the ontology map read from the 
                # database, if they do use the same IDs, else create them
                if (category not in observation_ont):
                    print("Cannot find {} in observation ontology.".format(category))
                    # As the category ID does not exist in the database create it
                    category_id = create_observation_ontology_term(cursor, category)
                    conn.commit()
    
                    observation_ont[category] = {'id': category_id, 'parent_id': 0}
                else:
                    category_id = observation_ont[category]['id']
    
                print("Category ID: {}".format(category_id))
    
                # Not every term has a scale, so check to see if the scale field is empty in 
                # which case use the category ID as the parent ID
                if scale == 'nan' or scale == 'NaN':
                    parent_id = category_id
                else:
                    # Check to see if the parent terms exist in the table, if not create them
                    if (scale not in observation_ont):
                        print("Cannot find {} in observation ontology.".format(scale))
                        # As the scale ID does not exist in the database create it
                        scale_id = create_observation_ontology_term(cursor, scale, category_id)
                        conn.commit()
    
                        observation_ont[scale] = {'id': scale_id, 'parent_id': 0}
                    else:
                        scale_id = observation_ont[scale]['id']
                
                    # As the scale exists, set the parent ID to scale ID
                    parent_id = scale_id

                # Check to see if the observation variable exists, if not create it    
                # If it does update it, else create a new entry
                observation_ont_id = get_observation_ontology(cursor, observation_term)
                print("observation variable: {} ontology ID: {}\n".format(observation_term, observation_ont_id))
                if (observation_ont_id == 0):
                    # As the observation_ont ID does not exist in the database create it
                    observation_ont_id = create_observation_ontology_term(cursor, observation_term, parent_id, value_type, data_category, flip_axis)
                    conn.commit()
                    observation_ont[observation_term] = {'id': category_id, 'parent_id': parent_id}
                else:
                    # As the ontology ID exists, update the ontology record
                    update_observation_ontology_term(cursor, observation_ont_id, observation_term, parent_id, value_type, data_category, flip_axis) 
                    conn.commit()


# Process the subject info file and either create an entry in the table or update the entry for 
# the subject from the demographics file with the following columns
# SubjectNum,SubjectVar,Value
# project_name	project_description	primary_diease	study_name	longitudinal	study_description
def process_subject_info(cursor, conn, project_file, study_map, subject_ont, df_col_names_field_map):

    pp.pprint(study_map)
    pp.pprint(subject_ont)

    # Create a lookup from column name to field name
    colname_to_fields = {}
    colname_to_data_type = {}
    for index, row in df_col_names_field_map.iterrows():
        # pp.pprint("Row: {} Index: {}".format(row, index))
        col_name = row['FieldName']
        data_type = row['Type']
        field_name = index
        colname_to_fields[col_name] = field_name
        colname_to_data_type[col_name] = data_type

    pp.pprint(colname_to_fields)

    # Open the file an iterate over the list
    with open(project_file) as ifh:
        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            # from ppmi_projects.csv
            # pp.pprint(row)
            subject_num = row['SubjectNum']
            subject_var = row['SubjectVar']
            value = row['Value']

            print("Processing subject num: {} variable: {} value: {}".format(subject_num, subject_var, value))

            # If the subject variable is "Study" then create an entry in the subject table
            if subject_var == "Study":
                if value in study_map.keys(): 
                    study_id = study_map[value] 
                else:
                    print ("Could not find study name {} in study map. Skipping ....".format(value))
                    continue

                # Check to see if the subject already exists in the database, if so add to subject map
                # else create one
                subject_id = get_subject_entry(cursor, subject_num, study_id)
                if subject_id == 0:
                    subject_id = create_subject_entry(cursor, subject_num, study_id)
                    conn.commit()
                
                # Add entry in subject map    
                subject_map[subject_num] = {"id": subject_id, "study_id": study_id}
            else:
                # For the column name lookup the field name
                if subject_var in colname_to_fields: 
                    sub_ont_label = colname_to_fields[subject_var]
                    value_type = colname_to_data_type[subject_var]
                else:
                    print ("Could not find subject variable {} in colname to fields. Skipping ....".format(subject_var))
                    continue

                # As the subject variable is not "Study" create an entry in the subject_attribute
                # table
                if sub_ont_label in subject_ont.keys(): 
                    subject_ont_id = subject_ont[sub_ont_label]["id"]
                else:
                    print ("Could not find subject variable {} in subject ontology. Skipping ....".format(sub_ont_label))
                    continue

                if subject_num in subject_map.keys(): 
                    study_id = subject_map[subject_num]["study_id"]
                    subject_id = subject_map[subject_num]["id"] 
                else:
                    print ("Could not find subject {} in subject map. Skipping ....".format(subject_num))
                    continue

                # Check to see if this subject attribute already exists, in which case update it,
                # else add it
                print("Processing variable {} with value: {} for subject ID: {} with subject ont : {}".format(sub_ont_label, value, subject_id, subject_ont_id))
                subj_attr_id = get_subject_attribute(cursor, subject_id, subject_ont_id)
                if (subj_attr_id == 0):
                    # Add the entry for this subject attribute
                    add_subject_attribute(cursor, subject_id, subject_ont_id, value, value_type)
                    conn.commit()
                else:
                    # As this entry already exists, update the fields
                    update_subject_attribute(cursor, subject_id, subject_ont_id, value, value_type)
                    conn.commit()

def get_subject_attribute(cursor, subject_id, subject_ont_id):
    attr_id = 0

    query = "SELECT id FROM subject_attribute where subject_id = {} and subject_ontology_id = {}".format(subject_id, subject_ont_id)
    print("Executing query: '{}'".format(query))
    try:
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            attr_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()
    
    print("Returning subject attribute ID: {}".format(attr_id))
    return attr_id    

def add_subject_attribute(cursor, subject_id, ont_id, val, val_type):
    if val_type == 'Char':
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type) VALUES ({}, {}, '{}', '{}')"
        query = query.format(subject_id, ont_id, val, val_type)
    elif val_type == 'Decimal':
        dec_value = Decimal(val)
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type, dec_value) VALUES ({}, {}, '{}', '{}', {})"
        query = query.format(subject_id, ont_id, val, val_type, dec_value)
    elif val_type == 'Integer':
        int_value = int(val)
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type, int_value) VALUES ({}, {}, '{}', '{}', {})"
        query = query.format(subject_id, ont_id, val, val_type, int_value)
    elif val_type == 'Date':
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type, date_value) VALUES ({}, {}, '{}', '{}', '{}')"
        query = query.format(subject_id, ont_id, val, val_type, val)
    else:
        print("Unknown value type {} skipping this entry".format(val_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)

    except Exception as e:
        print(e)
        sys.exit()

def update_subject_attribute(cursor, subject_id, ont_id, val, val_type):
    if val_type == 'Char':
        query = "UPDATE subject_attribute SET value = '{}', value_type = '{}' where subject_id = {} and subject_ontology_id = {}"
        query = query.format(val, val_type, subject_id, ont_id)
    elif val_type == 'Decimal':
        dec_value = Decimal(val)
        query = "UPDATE subject_attribute SET value = '{}', value_type = '{}', dec_value = {} where subject_id = {} and subject_ontology_id = {}"
        query = query.format(val, val_type, dec_value, subject_id, ont_id)
    elif val_type == 'Integer':
        int_value = int(val)
        query = "UPDATE subject_attribute SET value = '{}', value_type = '{}', int_value = {} where subject_id = {} and subject_ontology_id = {}"
        query = query.format(val, val_type, int_value, subject_id, ont_id)
    elif val_type == 'Date':
        query = "UPDATE subject_attribute SET value = '{}', value_type = '{}', date_value = '{}' where subject_id = {} and subject_ontology_id = {}"
        query = query.format(val, val_type, val, subject_id, ont_id)
    else:
        print("Unknown value type {} skipping this entry".format(val_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)

    except Exception as e:
        print(e)
        sys.exit()

def get_subject_ontology(cursor, label):
    ont_id = 0
    label = label.replace("'", "''")

    query = "SELECT id, label, parent_id FROM subject_ontology where label = '{}'".format(label)
    print("Executing query: '{}'".format(query))
    try:
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            ont_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()

    return ont_id    

# Method to create and entry in the subject ontology table
def create_subject_ontology_term(cursor, term, parent_id = None, value_type = None, data_category = None):
    ont_id = 0
    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "INSERT INTO subject_ontology (label) VALUES ('{}')"
            query = query.format(term)
        else:
            query = "INSERT INTO subject_ontology (label, parent_id) VALUES ('{}', {})"
            query = query.format(term, parent_id)

    else:
        query = "INSERT INTO subject_ontology (label, value_type, data_category, parent_id) VALUES ('{}', '{}', '{}', {})"
        query = query.format(term, value_type, data_category, parent_id)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)
        ont_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created ont entry '{}' in database with ID: {}.".format(term, ont_id))
    return ont_id

# Method to update and entry in the subject ontology table
def update_subject_ontology_term(cursor, subject_ont_id, term, parent_id = None, value_type = None, data_category = None):
    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "UPDATE subject_ontology set label = '{}' where id = {}"
            query = query.format(term, subject_ont_id)
        else:
            query = "UPDATE subject_ontology set label = '{}', parent_id = {} where id = {}"
            query = query.format(term, parent_id, subject_ont_id)

    else:
        query = "UPDATE subject_ontology set label = '{}', value_type = '{}', data_category = '{}', parent_id = {} where id = {}"
        query = query.format(term, value_type, data_category, parent_id, subject_ont_id)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated ontology entry '{}' in database with ID: {}.".format(term, subject_ont_id))

def get_observation_ontology(cursor, label):
    ont_id = 0
    label = label.replace("'", "''")

    query = "SELECT id, label, parent_id FROM observation_ontology where label = '{}'".format(label)
    print("Executing query: '{}'".format(query))
    try:
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            ont_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()

    return ont_id    

# Method to create and entry in the observation ontology table
def create_observation_ontology_term(cursor, term, parent_id = None, value_type = None, 
                                        data_category = None, flip_axis = 0):
    # If flip axis is nan then set to zero
    if str(flip_axis) == 'nan':
        flip_axis = 0

    ont_id = 0
    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "INSERT INTO observation_ontology (label) VALUES ('{}')"
            query = query.format(term)
        else:
            query = "INSERT INTO observation_ontology (label, parent_id) VALUES ('{}', {})"
            query = query.format(term, parent_id)

    else:
        query = "INSERT INTO observation_ontology (label, value_type, data_category, parent_id, flip_axis) VALUES ('{}', '{}', '{}', {}, {})"
        query = query.format(term, value_type, data_category, parent_id, flip_axis)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)
        ont_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created ont entry '{}' in database with ID: {}.".format(term, ont_id))
    return ont_id    

# Method to update and entry in the observation ontology table
def update_observation_ontology_term(cursor, observation_ont_id, term, parent_id = None, value_type = None, 
                                        data_category = None, flip_axis = 0):

    # If flip axis is nan then set to zero
    if str(flip_axis) == 'nan':
        flip_axis = 0

    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "UPDATE observation_ontology set label = '{}' where id = {}"
            query = query.format(term, observation_ont_id)
        else:
            query = "UPDATE observation_ontology set label = '{}', parent_id = {} where id = {}"
            query = query.format(term, parent_id, observation_ont_id)

    else:
        query = "UPDATE observation_ontology set label = '{}', value_type = '{}', data_category = '{}', parent_id = {}, flip_axis = {} where id = {}"
        query = query.format(term, value_type, data_category, parent_id, flip_axis, observation_ont_id)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated ontology entry '{}' in database with ID: {}.".format(term, observation_ont_id))

def add_observation_ontology_term(cursor, ont, term, parent_id=None):
    query = "INSERT INTO observation_ontology (label, parent_id) VALUES (%s, %s)"
    cursor.execute(query, (term, parent_id))
    ont[term] = {'id': cursor.lastrowid, 'parent_id': parent_id}

# Method that checks for the study in the database and returns the study ID, else zero
def get_study_entry(cursor, study_name, label):
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

# Method that inserts the study in the database and returns the study ID
def create_study_entry(cursor, study_name, longitudinal, study_description, project_id):
    study_id = 0
    # because the study name, description might have an apostrophe escape it
    study_name = study_name.replace("'", "''")
    study_description = study_description.replace("'", "''")

    query = "insert into study (study_name, description, longitudinal, project_id) values ('{}', '{}', {}, {})".format(study_name, study_description, longitudinal, project_id)
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)
        study_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created study entry '{}' in database with ID: {}.".format(study_name, study_id))
    return study_id


# Method that updates the study in the database and returns the study ID
def update_study_entry(cursor, study_id, study_name, longitudinal, study_description, project_id):
    # because the study name, description might have an apostrophe escape it
    study_name = study_name.replace("'", "''")
    study_description = study_description.replace("'", "''")

    query = "update study set study_name = '{}', description = '{}', longitudinal = {}, project_id = {} where id = {}".format(study_name, study_description, longitudinal, project_id, study_id)
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated study entry '{}' in database with ID: {}.".format(study_name, study_id))

# Method that retrieves a project ID if a project with the specified name exists
def get_project_entry(cursor, project_name):
    project_id = 0
    # because the project name, description, or disease name might have an apostrophe escape it
    project_name = project_name.replace("'", "''")

    query = "select id from project where project_name = '{}'".format(project_name)
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            project_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()

    print("Returning project ID: {}".format(project_id))
    return project_id

# Method that inserts the project in the database and returns the project ID
def create_project_entry(cursor, project_name, primary_disease, project_description):
    project_id = 0
    # because the project name, description, or disease name might have an apostrophe escape it
    project_name = project_name.replace("'", "''")
    primary_disease = primary_disease.replace("'", "''")
    project_description = project_description.replace("'", "''")

    query = "insert into project (project_name, project_description, primary_diease) values ('{}', '{}', '{}')".format(project_name, project_description, primary_disease)
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)
        project_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created project entry '{}' in database with ID: {}.".format(project_name, project_id))
    return project_id

# Method that update the project in the database 
def update_project_entry(cursor, project_id, project_name, primary_disease, project_description):
    # because the project name, description, or disease name might have an apostrophe escape it
    project_name = project_name.replace("'", "''")
    primary_disease = primary_disease.replace("'", "''")
    project_description = project_description.replace("'", "''")

    query = "update project set project_name = '{}', description = '{}', primary_disease = '{}' where id = {}".format(project_name, project_description, primary_disease, project_id)
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated project entry '{}' in database with ID: {}.".format(project_name, project_id))

# Method that inserts the subject in the database and returns the subject ID
def create_subject_entry(cursor, subject_num, study_id):
    subject_id = 0
    query = "insert into subject (subject_num, study_id) values ('{}', {})".format(subject_num, study_id)
    print("Executing query: {}".format(query))
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
def create_subject_visit(cursor, subject_id, visit_num, visit_code, visit_date, disease_status):
    visit_id = 0
    query = "insert into subject_visit (visit_num, subject_id, visit_event, event_date, disease_status) values ({}, {}, '{}', '{}', '{}')"
    query = query.format(visit_num, subject_id, visit_code, visit_date, disease_status)
    print("Executing query: {}".format(query))
    try:
        cursor.execute(query)
        visit_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject visit '{}' in database with subject ID: {}.".format(visit_num, subject_id))
    return visit_id

# Method that updates the visit in the database and returns the visit ID
def update_subject_visit(cursor, subject_visit_id, visit_code, visit_date, disease_status):
    query = "update subject_visit set visit_event = '{}', event_date = '{}', disease_status = '{}' where id = {}"
    query = query.format(visit_code, visit_date, disease_status, subject_visit_id)
    print("Executing query: {}".format(query))
    try:
        cursor.execute(query)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated subject visit ID {} in database.".format(subject_visit_id))

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

def get_observation_ontology_info(conn):
    query = 'SELECT id, label, parent_id, value_type, flip_axis FROM observation_ontology'
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(e)
        sys.exit()

    return df

def get_subject_ontology_info(conn):
    query = "SELECT id, label, parent_id FROM subject_ontology"
    try:
        df = pd.read_sql_query(query, conn)

    except Exception as e:
        print(e)
        sys.exit()

    return df

def get_project_info(conn):
    query = "SELECT id, project_name, user_id, project_url, primary_disease, is_public, description from project" 
    try:
        df = pd.read_sql_query(query, conn)

    except Exception as e:
        print(e)
        sys.exit()

    return df

def get_study_info(conn):
    query = "SELECT id, study_name, project_id, longitudinal, description from study" 
    try:
        df = pd.read_sql_query(query, conn)

    except Exception as e:
        print(e)
        sys.exit()

    return df

# Method that checks for the visit in the database and returns the visit ID, else zero
def get_subject_visit(cursor, subject_id, visit_num):
    visit_id = 0
    # First check if this visit already exists in which case just read the visit ID and return it
    query = "SELECT id FROM subject_visit where visit_num = {} AND subject_id = {}".format(visit_num, subject_id)
    try:
        print("Executing query: {}".format(query))
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            visit_id = row[0]
    except Exception as e:
        print(e)
        sys.exit()
    print("Returning visit ID: {}".format(visit_id))
    return visit_id

# Method that checks for the subject in the database and returns the subject ID, else zero
def get_subject_entry(cursor, subject_num, study_id):
    subject_id = 0
    # First check if this entry already exists in which case just read the subject ID and return it
    query = "SELECT id FROM subject where subject_num = '{}' AND study_id = {}".format(subject_num, study_id)
    print ("Executing query: {}".format(query))
    try:
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            subject_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()
    print("Returning subject ID: {} for Subject Num: {}".format(subject_id, subject_num))
    return subject_id




if __name__ == '__main__':
    main()
