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
import os
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
    df_entity_file_map = pd.read_csv(args.input_file, index_col="Entity")
    pp.pprint(df_entity_file_map)

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
    has_longitudinal_data = False
    
    entities = ["Project", "Subject Ontology", "Observation Ontology", "Subject Info", "Visit", "Observations", "Observations Summary"]
    for entity in entities:
        # allow Observations Summary to be absent
        if (entity not in df_entity_file_map) and (entity == 'Observations Summary'):
            continue
        entity_file = df_entity_file_map.loc[entity]['File']
        pp.pprint(entity_file)
        entity_file = os.path.join(args.input_dir, entity_file)
        print("Processing entity: %s file: %s" % (entity, entity_file))
        if entity is "Project":
            print("Processing project and studies .....")
            has_longitudinal_data = process_projects_and_studies(cursor, conn, entity_file, df_project_info, df_study_info, df_col_names_field_map)
        elif entity is "Subject Ontology":
            print("Processing subject ontology .....")
            process_subject_ontology(cursor, conn, entity_file, subject_ont, df_col_names_field_map)
        elif entity is "Observation Ontology":
            print("Processing observation ontology .....")
            process_observation_ontology(cursor, conn, entity_file, observation_ont, df_col_names_field_map)
        elif entity is "Subject Info":
            print("Processing subject information .....")
            process_subject_info(cursor, conn, entity_file, study_map, subject_ont, df_col_names_field_map)
            #exit()
        elif entity is "Visit":
            print("Processing visit information .....")
            process_subject_visits(cursor, conn, entity_file, df_col_names_field_map)
        elif entity is "Observations":
            print("Processing observations information .....")
            process_subject_observations(cursor, conn, entity_file, observation_ont, df_col_names_field_map)
        elif entity is "Observations Summary":
            print("Processing observations summary information, has_longitudinal_data=" + str(has_longitudinal_data) + " .....")
            if has_longitudinal_data:
                process_subject_obs_summary(cursor, conn, entity_file, observation_ont, df_col_names_field_map)
            else:
                continue
                
# Process the subject visits file to create or update entries inthe subject_visit table
# tables. The file has the following columns:
# SubjectNum,VisitCode,VisitDate

def process_subject_visits(cursor, conn, visit_file, df_col_names_field_map):

    pp.pprint(subject_map)

    # Open the file and iterate over the list
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
            disease_status = ""

            if subject_num in subject_map:
                subject_info = subject_map[subject_num]
                subject_id = subject_info["id"]
            else:
                print("Cannot find subject num {} in subject map. Skipping entry .....".format(subject_num))
                continue

            print("Processing subject: {} ID: {} Visit Code: {} Visit Date: {} Visit Num: {}".format(subject_num, subject_id, visit_code, visit_date, visit_num))

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


# Process the subject observations file to create or update entries in the observation table
# The file has the following columns:
# SubjectNum,VisitCode,VisitDate
def process_subject_observations(cursor, conn, obs_file, observation_ont, df_col_names_field_map):

    pp.pprint(subject_map)
    pp.pprint(observation_ont)
    pp.pprint(df_col_names_field_map)

    # Create a lookup from column name to field name
    colname_to_fields = {}
    colname_to_data_type = {}
    for index, row in df_col_names_field_map.iterrows():
        # pp.pprint("Row: {} Index: {}".format(row, index))
        testname = row['Testname']
        data_type = row['Type']
        field_name = index
        if (testname):
            key = testname
        else:
            key = index 
        print("Key for this map is: {}".format(key))

        colname_to_fields[key] = field_name
        colname_to_data_type[key] = data_type

    pp.pprint(colname_to_fields)
    pp.pprint(colname_to_data_type)

    # Open the file and iterate over the list
    with open(obs_file) as ifh:

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            # from ppmi_projects.csv
            pp.pprint(row)
            subject_num = row['SubjectNum']
            testname = row['Testname']
            value = row['Value']
            visit_num = row['VisitNum']

            if subject_num in subject_map:
                subject_info = subject_map[subject_num]
                subject_id = subject_info["id"]
            else:
                print("WARN: Cannot find subject num {} in subject map. Skipping entry .....".format(subject_num))
                continue

            # If no visits have been processed yet then warn
            if ('visits' not in subject_info):
                print("WARN: Cannot find subject visits {} in subject map. Skipping entry .....".format(subject_num))
                continue
            else:
                subject_visits = subject_info['visits']
                if visit_num in subject_visits:
                    subject_visit_id = subject_visits[visit_num]
                else:
                    print("WARN: Cannot find subject visit number {} in visits. Skipping entry .....".format(visit_num))
                    continue


            print("Subject: {} ID: {} Visit Num: {} Testname: {} Value: {}".format(subject_num, subject_id, visit_num, testname, value))
            observation_term = colname_to_fields[testname]
            value_type = colname_to_data_type[testname]

            if observation_term in observation_ont:
                obs_ont_id = observation_ont[observation_term]["id"]
            else:
                print("WARN: Cannot find testname {} in observation ontology. Skipping entry .....".format(testname))
                continue

            # Check to see if this observation already exists in database, if so use the ID
            # else create an entry
            obs_id = 0
            obs_id = get_subject_observation(cursor, subject_visit_id, obs_ont_id)
            if (obs_id == 0):
                print("Creating entry.")
                # As the subject visit entry does not exist in database create it
                obs_id = create_subject_observation(cursor, subject_visit_id, obs_ont_id, value, value_type) 
                conn.commit()
            else:
                print("Updating entry.")
                update_subject_observation(cursor, subject_visit_id, obs_ont_id, value, value_type) 
                conn.commit()


# Process the subject observations summary file to create or update entries in the observation_summary table
# The file has the following columns:
# SubjectNum,VisitCode,VisitDate
def process_subject_obs_summary(cursor, conn, obs_file, observation_ont, df_col_names_field_map):

    pp.pprint(subject_map)
    pp.pprint(observation_ont)
    pp.pprint(df_col_names_field_map)

    # Create a lookup from column name to field name
    colname_to_fields = {}
    colname_to_data_type = {}
    for index, row in df_col_names_field_map.iterrows():
        # pp.pprint("Row: {} Index: {}".format(row, index))
        testname = row['Testname']
        data_type = row['Type']
        field_name = index
        if (testname):
            key = testname
        else:
            key = index 
        print("Key for this map is: {}".format(key))

        colname_to_fields[key] = field_name
        colname_to_data_type[key] = data_type

    pp.pprint(colname_to_fields)
    pp.pprint(colname_to_data_type)

    # Open the file and iterate over the list
    with open(obs_file) as ifh:

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            # from ppmi_projects.csv
            pp.pprint(row)
            subject_num = row['SubjectNum']
            testname = row['Testname']
            value = row['Value']

            if subject_num in subject_map:
                subject_info = subject_map[subject_num]
                subject_id = subject_info["id"]
            else:
                print("WARN: Cannot find subject num {} in subject map. Skipping entry .....".format(subject_num))
                continue

            observation_term = colname_to_fields[testname]
            value_type = colname_to_data_type[testname]
            print("Subject: {} ID: {} Testname: {} Value: {} Observation Ontology: {} Value Type: {}".format(subject_num, subject_id, testname, value,
                                                                                                            observation_term, value_type))

            if observation_term in observation_ont:
                obs_ont_id = observation_ont[observation_term]["id"]
            else:
                print("WARN: Cannot find testname {} in observation ontology. Skipping entry .....".format(testname))
                continue

            # Check to see if this observation already exists in database, if so use the ID
            # else create an entry
            obs_id = 0
            obs_id = get_subject_obs_summary(cursor, subject_id, obs_ont_id)
            if (obs_id == 0):
                print("Creating entry.")
                # As the subject visit entry does not exist in database create it
                obs_id = create_subject_obs_summary(cursor, subject_id, obs_ont_id, value, value_type) 
                conn.commit()
            else:
                print("Updating entry.")
                update_subject_obs_summary(cursor, subject_id, obs_ont_id, value, value_type) 
                conn.commit()

# Process the projects file and create missing entries or update existing entries in the 'project' and 'study'
# tables. The file has the following columns:
# project_name	project_description	primary_diease	study_name	longitudinal	study_description
def process_projects_and_studies(cursor, conn, project_file, df_project_info, df_study_info, df_col_names_field_map):
    has_longitudinal_data = False

    # Open the file and iterate over the list
    with open(project_file, encoding = 'utf-8-sig') as ifh:

        # dialect = csv.Sniffer().sniff(ifh.read(1024))
        # ifh.seek(0)
        # next(ifh) # Skip the header line

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            # from ppmi_projects.csv
            ##does longitudinal need to be changed?##
            pp.pprint(row)
            project_name = row['project_name']
            project_description = row['project_description']
            primary_disease = row['primary_disease']
            study_name = row['study_name']
            longitudinal = row['longitudinal']
            study_description = row['study_description'] 
            if longitudinal == '1':
                has_longitudinal_data = True
                
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

    return has_longitudinal_data
                
# Process the subject ontology file to create or update entries in the 'subject_ontology'
# table. The file has the following columns:
# Observations
def process_subject_ontology(cursor, conn, subject_ont_file, subject_ont, df_col_names_field_map):

    # Open the file and iterate over the list
    with open(subject_ont_file) as ifh:
        # dialect = csv.Sniffer().sniff(ifh.read(1024))
        # ifh.seek(0)
        # next(ifh) # Skip the header line

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:
            abbrevation = None
            label = None
            description = None

            # 3-column format - SubjectVar, Label, Description
            abbreviation = row['SubjectVar']
            if row['Label'] == '':
                label = abbreviation
            else:
                label = row['Label']
            description = row['Description']
            
            print("Processing variable: {}".format(label))

            # Look for this observation in the field map
            #if df_col_names_field_map.isin([subject_var]).any().empty:
            #   print("Variable {} is not in mapping file, skipping ....".format(subject_var))
            #  continue

            map_row = df_col_names_field_map.loc[label]
            database_entity = map_row['Database Entity']
            value_type = map_row['Type']
            data_category = map_row['Data Type']
            category = map_row['Category']
            scale = str(map_row['Scale'])

            # Make sure that the variable belongs to the subject_ontology table, else skip
            # For instance the variable Study does not belong, so skip
            if (database_entity != "subject_ontology"):
                print("Variable {} is not in subject ontology, skipping ....".format(label))
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
                category_id = create_subject_ontology_term(cursor, category, category, None)
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
                    scale_id = create_subject_ontology_term(cursor, scale, abbreviation, description, category_id)
                    conn.commit()

                    subject_ont[scale] = {'id': scale_id, 'parent_id': 0}
                else:
                    scale_id = subject_ont[scale]['id']
                
                # As the scale exists, set the parent ID to scale ID
                parent_id = scale_id

            # Check to see if the subject variable exists, if not create it    
            # If it does update it, else create a new entry
            subject_ont_id = get_subject_ontology(cursor, label)
            print("Subject variable: {} ontology ID: {}\n".format(label, subject_ont_id))
            if (subject_ont_id == 0):
                # As the subject_ont ID does not exist in the database create it
                subject_ont_id = create_subject_ontology_term(cursor, label, abbreviation, description, parent_id, value_type, data_category)
                conn.commit()
                subject_ont[label] = {'id': subject_ont_id, 'parent_id': parent_id}
            else:
                # As the ontology ID exists, update the ontology record
                update_subject_ontology_term(cursor, subject_ont_id, label, abbreviation, description, parent_id, value_type, data_category) 
                conn.commit()


# Process the observation ontology file to create or update entries in the 'observation_ontology'
# table. The file has the following columns:
# Observations
def process_observation_ontology(cursor, conn, observation_ont_file, observation_ont, df_col_names_field_map):
    #pp.pprint(df_col_names_field_map)
    # Open the file and iterate over the list
    with open(observation_ont_file) as ifh:
        # dialect = csv.Sniffer().sniff(ifh.read(1024))
        # ifh.seek(0)
        # next(ifh) # Skip the header line

        reader = csv.DictReader(ifh)

        # Process the remaining lines
        for row in reader:

            # 3-columns expected - Testname, Label, Description
            abbreviation = row['Testname']
            if row['Label'] == '':
                label = abbreviation
            else:
                label = row['Label']
            description = row['Description']

            print("Processing variable: {}".format(label))

            # Look for this observation in the field map
            # Because an observation could have summary values we have to handle thos as well
            # For instance Semantic Fluency has observations, but may also have change and ROC
            # as additional observation summary values that need to be handled
            map_rows = df_col_names_field_map.loc[df_col_names_field_map['Testname'] == abbreviation]
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
                    category_id = create_observation_ontology_term(cursor, category, category, None)
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
                        scale_id = create_observation_ontology_term(cursor, scale, scale, None, category_id)
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
                    observation_ont_id = create_observation_ontology_term(cursor, observation_term, abbreviation, description, parent_id, value_type, data_category, flip_axis)
                    conn.commit()
                    observation_ont[observation_term] = {'id': observation_ont_id, 'parent_id': parent_id}
                else:
                    # As the ontology ID exists, update the ontology record
                    update_observation_ontology_term(cursor, observation_ont_id, observation_term, abbreviation, description, parent_id, value_type, data_category, flip_axis) 
                    conn.commit()


# Process the subject info file and either create an entry in the table or update the entry for 
# the subject from the demographics file with the following columns
# SubjectNum,SubjectVar,Value
# project_name	project_description	primary_diease	study_name	longitudinal	study_description
def process_subject_info(cursor, conn, subject_file, study_map, subject_ont, df_col_names_field_map):

    pp.pprint(study_map)
    pp.pprint(subject_ont)

    # Create a lookup from column name to field name
    colname_to_fields = {}
    colname_to_data_type = {}
    for index, row in df_col_names_field_map.iterrows():
        # pp.pprint("Row: {} Index: {}".format(row, index))
        col_name = row['Testname']
        data_type = row['Type']
        field_name = index
        colname_to_fields[col_name] = field_name
        colname_to_data_type[col_name] = data_type

    pp.pprint(colname_to_fields)
    subject_vars = []

    # Open the file and iterate over the list
    with open(subject_file) as ifh:
        reader = csv.DictReader(ifh)

        for row in reader:
            subject_num = row['SubjectNum']
            subject_var = row['SubjectVar']
            value = row['Value']

            # If the subject variable is "Study" then create an entry in the subject table
            if subject_var == "Study":
                print("Processing subject num: {} variable: {} value: {}".format(subject_num, subject_var, value))

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

            # If the subject variable is not "Study" then save the row for processing after all subjects are created
            else:
                subject_vars.append((subject_num, subject_var, value))

        # Process everything except "Study" variable assignments
        for sv in subject_vars:
            (subject_num, subject_var, value) = sv
            print("Processing subject num: {} variable: {} value: {}".format(subject_num, subject_var, value))

            # For the column name look up the field name
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

    query = "SELECT id FROM subject_attribute where subject_id = %s and subject_ontology_id = %s"
    print("Executing query: '{}'".format(query))
    try:
        cursor.execute(query, (subject_id, subject_ont_id))

        row = cursor.fetchone()
        if row is not None:
            attr_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()
    
    print("Returning subject attribute ID: {}".format(attr_id))
    return attr_id    

def add_subject_attribute(cursor, subject_id, ont_id, val, val_type):
    query_args = ()
    if val_type == 'Char':
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type) VALUES (%s, %s, %s, %s)"
        query_args = (subject_id, ont_id, val, val_type)
    elif val_type == 'Decimal':
        dec_value = Decimal(val)
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type, dec_value) VALUES (%s, %s, %s, %s, %s)"
        query_args = (subject_id, ont_id, val, val_type, dec_value)
    elif val_type == 'Integer':
        int_value = int(val)
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type, int_value) VALUES (%s, %s, %s, %s, %s)"
        query_args = (subject_id, ont_id, val, val_type, int_value)
    elif val_type == 'Date':
        query = "INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type, date_value) VALUES (%s, %s, %s, %s, %s)"
        query_args = (subject_id, ont_id, val, val_type, val)
    else:
        print("Unknown value type {} skipping this entry".format(val_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)

    except Exception as e:
        print(e)
        sys.exit()

def update_subject_attribute(cursor, subject_id, ont_id, val, val_type):
    query_args = ()
    if val_type == 'Char':
        query = "UPDATE subject_attribute SET value = %s, value_type = %s where subject_id = %s and subject_ontology_id = %s"
        query_args = (val, val_type, subject_id, ont_id)
    elif val_type == 'Decimal':
        dec_value = Decimal(val)
        query = "UPDATE subject_attribute SET value = %s, value_type = %s, dec_value = %s where subject_id = %s and subject_ontology_id = %s"
        query_args = (val, val_type, dec_value, subject_id, ont_id)
    elif val_type == 'Integer':
        int_value = int(val)
        query = "UPDATE subject_attribute SET value = %s, value_type = %s, int_value = %s where subject_id = %s and subject_ontology_id = %s"
        query_args = (val, val_type, int_value, subject_id, ont_id)
    elif val_type == 'Date':
        query = "UPDATE subject_attribute SET value = %s, value_type = %s, date_value = %s where subject_id = %s and subject_ontology_id = %s"
        query_args = (val, val_type, val, subject_id, ont_id)
    else:
        print("Unknown value type {} skipping this entry".format(val_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)

    except Exception as e:
        print(e)
        sys.exit()

def get_subject_ontology(cursor, label):
    ont_id = 0
    query = "SELECT id, label, parent_id FROM subject_ontology where label = %s"
    print("Executing query: '{}'".format(query))
    try:
        cursor.execute(query, (label,))

        row = cursor.fetchone()
        if row is not None:
            ont_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()

    return ont_id    

# Method to create and entry in the subject ontology table
def create_subject_ontology_term(cursor, term, abbreviation, description, parent_id = None, value_type = None, data_category = None):
    query_args = ()
    ont_id = 0
    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "INSERT INTO subject_ontology (label, abbreviation, description) VALUES (%s, %s, %s)"
            query_args = (term, abbreviation, description)
        else:
            query = "INSERT INTO subject_ontology (label, parent_id, abbreviation, description) VALUES (%s, %s, %s, %s)"
            query_args = (term, parent_id, abbreviation, description)

    else:
        query = "INSERT INTO subject_ontology (label, value_type, data_category, parent_id, abbreviation, description) VALUES (%s, %s, %s, %s, %s, %s)"
        query_args = (term, value_type, data_category, parent_id, abbreviation, description)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)
        ont_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created ont entry '{}' in database with ID: {}.".format(term, ont_id))
    return ont_id

# Method to update and entry in the subject ontology table
def update_subject_ontology_term(cursor, subject_ont_id, term, abbreviation, description, parent_id = None, value_type = None, data_category = None):
    query_args = ()
    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "UPDATE subject_ontology set label = %s, abbreviation = %s, description = %s where id = %s"
            query_args = (term, abbreviation, description, subject_ont_id)
        else:
            query = "UPDATE subject_ontology set label = %s, abbreviation = %s, description = %s, parent_id = %s where id = %s"
            query_args = (term, abbreviation, description, parent_id, subject_ont_id)

    else:
        query = "UPDATE subject_ontology set label = %s, abbreviation = %s, description = %s, value_type = %s, data_category = %s, parent_id = %s where id = %s"
        query_args = (term, abbreviation, description, value_type, data_category, parent_id, subject_ont_id)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated ontology entry '{}' in database with ID: {}.".format(term, subject_ont_id))

def get_observation_ontology(cursor, label):
    ont_id = 0
    query = "SELECT id, label, parent_id FROM observation_ontology where label = %s"
    print("Executing query: '{}'".format(query))
    try:
        cursor.execute(query, (label,))

        row = cursor.fetchone()
        if row is not None:
            ont_id = row[0]

    except Exception as e:
        print(e)
        sys.exit()

    return ont_id    

# Method to create and entry in the observation ontology table
def create_observation_ontology_term(cursor, term, abbreviation, description, parent_id = None, value_type = None, 
                                     data_category = None, flip_axis = 0):
    query_args = ()
    # If flip axis is nan then set to zero
    if str(flip_axis) == 'nan':
        flip_axis = 0

    ont_id = 0
    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "INSERT INTO observation_ontology (label, abbreviation, description) VALUES (%s, %s, %s)"
            query_args = (term, abbreviation, description)
        else:
            query = "INSERT INTO observation_ontology (label, parent_id, abbreviation, description) VALUES (%s, %s, %s, %s)"
            query_args = (term, parent_id, abbreviation, description)

    else:
        query = "INSERT INTO observation_ontology (label, value_type, data_category, parent_id, abbreviation, description, flip_axis) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        query_args = (term, value_type, data_category, parent_id, abbreviation, description, flip_axis)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)
        ont_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created ont entry '{}' in database with ID: {}.".format(term, ont_id))
    return ont_id    

# Method to update and entry in the observation ontology table
def update_observation_ontology_term(cursor, observation_ont_id, term, abbreviation, description, parent_id = None, value_type = None, 
                                     data_category = None, flip_axis = 0):

    query_args = ()
    
    # If flip axis is nan then set to zero
    if str(flip_axis) == 'nan':
        flip_axis = 0

    # Sometimes value_type or data_category are missing when the label is a parent
    # in such cases skip inserting these columns
    if (value_type is None or data_category is None):
        # If the parent ID is None this must me a top level term so do not set parent ID
        if parent_id is None:
            query = "UPDATE observation_ontology set label = %s, abbreviation = %s, description = %s where id = %s"
            query_args = (term, abbreviation, description, observation_ont_id)
        else:
            query = "UPDATE observation_ontology set label = %s, abbreviation = %s, description = %s, parent_id = %s where id = %s"
            query_args = (term, abbreviation, description, parent_id, observation_ont_id)

    else:
        query = "UPDATE observation_ontology set label = %s, abbreviation = %s, description = %s, value_type = %s, data_category = %s, parent_id = %s, flip_axis = %s where id = %s"
        query_args = (term, abbreviation, description, value_type, data_category, parent_id, flip_axis, observation_ont_id)

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated ontology entry '{}' in database with ID: {}.".format(term, observation_ont_id))

def add_observation_ontology_term(cursor, ont, term, parent_id=None):
    query = "INSERT INTO observation_ontology (label, parent_id) VALUES (%s, %s)"
    cursor.execute(query, (term, parent_id))
    ont[term] = {'id': cursor.lastrowid, 'parent_id': parent_id}

# Method that checks for the study in the database and returns the study ID, else zero
def get_study_entry(cursor, study_name, project_id):
    study_id = 0
    # First check if this entry already exists in which case just read the study ID and return it
    query = "SELECT id FROM study where study_name = %s AND project_id = %s"
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (study_name, project_id))

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
    query = "insert into study (study_name, description, longitudinal, project_id) values (%s, %s, %s, %s)"
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (study_name, study_description, longitudinal, project_id))
        study_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created study entry '{}' in database with ID: {}.".format(study_name, study_id))
    return study_id


# Method that updates the study in the database and returns the study ID
def update_study_entry(cursor, study_id, study_name, longitudinal, study_description, project_id):
    query = "update study set study_name = %s, description = %s, longitudinal = %s, project_id = %s where id = %s"
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (study_name, study_description, longitudinal, project_id, study_id))

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated study entry '{}' in database with ID: {}.".format(study_name, study_id))

# Method that retrieves a project ID if a project with the specified name exists
def get_project_entry(cursor, project_name):
    project_id = 0
    query = "select id from project where project_name = %s"
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (project_name, ))

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
    query = "insert into project (project_name, description, primary_disease) values (%s, %s, %s)"
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (project_name, project_description, primary_disease))
        project_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created project entry '{}' in database with ID: {}.".format(project_name, project_id))
    return project_id

# Method that update the project in the database 
def update_project_entry(cursor, project_id, project_name, primary_disease, project_description):
    query = "update project set project_name = %s, description = %s, primary_disease = %s where id = %s"
    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, (project_name, project_description, primary_disease, project_id))

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated project entry '{}' in database with ID: {}.".format(project_name, project_id))

# Method that inserts the subject in the database and returns the subject ID
def create_subject_entry(cursor, subject_num, study_id):
    subject_id = 0
    query = "insert into subject (subject_num, study_id) values (%s, %s)"
    print("Executing query: {}".format(query))
    try:
        cursor.execute(query, (subject_num, study_id))
        subject_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject entry '{}' in database with ID: {}.".format(subject_num, study_id))
    return subject_id

# Method that inserts the observation in the database and returns the observation ID
def create_subject_observation(cursor, subject_visit_id, obs_ont_id, value, value_type):
    query_args = ()
    observation_id = 0    
    if value_type == 'Char':
        query = "INSERT INTO observation (subject_visit_id, observation_ontology_id, value, value_type) VALUES (%s, %s, %s, %s)"
        query_args = (subject_visit_id, obs_ont_id, value, value_type)
    elif value_type == 'Decimal':
        try:
            dec_value = Decimal(value)
        except InvalidOperation:
            print("WARN: invalid Decimal value '" + value + "', inserting NULL")
            dec_value = None
        query = "INSERT INTO observation (subject_visit_id, observation_ontology_id, value, value_type, dec_value) VALUES (%s, %s, %s, %s, %s)"
        query_args = (subject_visit_id, obs_ont_id, value, value_type, dec_value)
    elif value_type == 'Integer':
        int_value = int(value)
        query = "INSERT INTO observation (subject_visit_id, observation_ontology_id, value, value_type, int_value) VALUES (%s, %s, %s, %s, %s)"
        query_args = (subject_visit_id, obs_ont_id, value, value_type, int_value)
    elif value_type == 'Date':
# requires date_value column
#        query = "INSERT INTO observation (subject_visit_id, observation_ontology_id, value, value_type, date_value) VALUES (%s, %s, %s, %s, %s)"
#        query_args = (subject_visit_id, obs_ont_id, value, value_type, value)
        query = "INSERT INTO observation (subject_visit_id, observation_ontology_id, value, value_type) VALUES (%s, %s, %s, %s)"
        query_args = (subject_visit_id, obs_ont_id, value, value_type)
    else:
        print("Unknown value type {} skipping this entry".format(value_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)
        observation_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject observation '{}' in database with subject visit ID: {}.".format(obs_ont_id, subject_visit_id))
    return observation_id


# Method that update the observation in the database and returns the observation ID
def update_subject_observation(cursor, subject_visit_id, obs_ont_id, value, value_type):
    query_args = ()
    if value_type == 'Char':
        query = "update observation set value = %s, value_type = %s where subject_visit_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_visit_id, obs_ont_id)
    elif value_type == 'Decimal':
        dec_value = Decimal(value)
        query = "update observation set value = %s, value_type = %s, dec_value = %s where subject_visit_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_visit_id, obs_ont_id, dec_value)
    elif value_type == 'Integer':
        int_value = int(value)
        query = "update observation set value = %s, value_type = %s, int_value = %s where subject_visit_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_visit_id, obs_ont_id, int_value)
    elif value_type == 'Date':
# requires date_value column
#        query = "update observation set value = %s, value_type = %s, date_value = %s where subject_visit_id = %s and observation_ontology_id = %s"
#        query_args = (value, value_type, value, subject_visit_id, obs_ont_id)
        query = "update observation set value = %s, value_type = %s where subject_visit_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_visit_id, obs_ont_id)
    else:
        print("Unknown value type {} skipping this entry".format(value_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated subject observation '{}' in database with subject visit ID: {}.".format(obs_ont_id, subject_visit_id))

# Method that inserts the observation_summary in the database and returns the observation_summary ID
def create_subject_obs_summary(cursor, subject_id, obs_ont_id, value, value_type):
    query_args = ()
    obs_summary_id = 0    
    if value_type == 'Char':
        query = "INSERT INTO observation_summary (subject_id, observation_ontology_id, value, value_type) VALUES (%s, %s, %s, %s)"
        query_args = (subject_id, obs_ont_id, value, value_type)
    elif value_type == 'Decimal':
        dec_value = Decimal(value)
        query = "INSERT INTO observation_summary (subject_id, observation_ontology_id, value, value_type, dec_value) VALUES (%s, %s, %s, %s, %s)"
        query_args = (subject_id, obs_ont_id, value, value_type, dec_value)
    elif value_type == 'Integer':
        int_value = int(value)
        query = "INSERT INTO observation_summary (subject_id, observation_ontology_id, value, value_type, int_value) VALUES (%s, %s, %s, %s, %s)"
        query_args = (subject_id, obs_ont_id, value, value_type, int_value)
    elif value_type == 'Date':
# requires date_value column
#        query = "INSERT INTO observation_summary (subject_id, observation_ontology_id, value, value_type, date_value) VALUES (%s, %s, %s, %s, %s)"
#        query_args = (subject_id, obs_ont_id, value, value_type, value)
        query = "INSERT INTO observation_summary (subject_id, observation_ontology_id, value, value_type) VALUES (%s, %s, %s, %s)"
        query_args = (subject_id, obs_ont_id, value, value_type)
    else:
        print("Unknown value type {} skipping this entry".format(value_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)
        obs_summary_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject observation summary '{}' in database with subject ID: {}.".format(obs_ont_id, subject_id))
    return obs_summary_id


# Method that update the observation summary in the database 
def update_subject_obs_summary(cursor, subject_id, obs_ont_id, value, value_type):
    query_args = ()
    if value_type == 'Char':
        query = "update observation_summary set value = %s, value_type = %s where subject_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_id, obs_ont_id)
    elif value_type == 'Decimal':
        dec_value = Decimal(value)
        query = "update observation_summary set value = %s, value_type = %s, dec_value = %s where subject_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_id, obs_ont_id, dec_value)
    elif value_type == 'Integer':
        int_value = int(value)
        query = "update observation_summary set value = %s, value_type = %s, int_value = %s where subject_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_id, obs_ont_id, int_value)
    elif value_type == 'Date':
# requires date_value column
#        query = "update observation_summary set value = %s, value_type = %s, date_value = %s where subject_id = %s and observation_ontology_id = %s"
#        query_args = (value, value_type, value, subject_id, obs_ont_id)
        query = "update observation_summary set value = %s, value_type = %s where subject_id = %s and observation_ontology_id = %s"
        query_args = (value, value_type, subject_id, obs_ont_id)
    else:
        print("Unknown value type {} skipping this entry".format(value_type))
        return

    try:
        print("Executing query: '{}'".format(query))
        cursor.execute(query, query_args)

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated subject observation '{}' in database with subject ID: {}.".format(obs_ont_id, subject_id))

# Method that inserts the visit in the database and returns the visit ID
def create_subject_visit(cursor, subject_id, visit_num, visit_code, visit_date, disease_status):
    visit_id = 0
    if visit_date == '':
        visit_date = None
    query = "insert into subject_visit (visit_num, subject_id, visit_event, event_date, disease_status) values (%s, %s, %s, %s, %s)"
    print("Executing query: {}".format(query))
    try:
        cursor.execute(query, (visit_num, subject_id, visit_code, visit_date, disease_status))
        visit_id = cursor.lastrowid

    except Exception as e:
        print(e)
        sys.exit()

    print("Created subject visit '{}' in database with subject ID: {}.".format(visit_num, subject_id))
    return visit_id

# Method that updates the visit in the database and returns the visit ID
def update_subject_visit(cursor, subject_visit_id, visit_code, visit_date, disease_status):
    query = "update subject_visit set visit_event = %s, event_date = %s, disease_status = %s where id = %s"
    print("Executing query: {}".format(query))
    try:
        cursor.execute(query, (visit_code, visit_date, disease_status, subject_visit_id))

    except Exception as e:
        print(e)
        sys.exit()

    print("Updated subject visit ID {} in database.".format(subject_visit_id))

# Method that checks for the observation in the database and returns the observation ID, else zero
def get_subject_observation(cursor, subject_visit_id, obs_ont_id):
    observation_id = 0
    # First check if this observation already exists in which case just read the observation ID and return it
    query = "SELECT id FROM observation where observation_ontology_id = %s AND subject_visit_id = %s"
    print("Executing query: {}".format(query))
    try:
        cursor.execute(query, (obs_ont_id, subject_visit_id))

        row = cursor.fetchone()
        if row is not None:
            observation_id = row[0]
    except Exception as e:
        print(e)
        sys.exit()

    return observation_id


# Method that checks for the observation summary in the database and returns the observation summary ID, else zero
def get_subject_obs_summary(cursor, subject_id, obs_ont_id):
    obs_summary_id = 0
    # First check if this observation summary already exists in which case just read the observation summary ID and return it
    query = "SELECT id FROM observation_summary where observation_ontology_id = %s AND subject_id = %s"
    print("Executing query: {}".format(query))
    try:
        cursor.execute(query, (obs_ont_id, subject_id))

        row = cursor.fetchone()
        if row is not None:
            obs_summary_id = row[0]
    except Exception as e:
        print(e)
        sys.exit()

    return obs_summary_id

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
    query = "SELECT id FROM subject_visit where visit_num = %s AND subject_id = %s"
    try:
        print("Executing query: {}".format(query))
        cursor.execute(query, (visit_num, subject_id))

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
    query = "SELECT id FROM subject where subject_num = %s AND study_id = %s"
    print ("Executing query: {}".format(query))
    try:
        cursor.execute(query, (subject_num, study_id))

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
