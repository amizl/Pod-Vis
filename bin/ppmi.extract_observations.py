#!/usr/bin/env python3

"""

This script is used to parse the PPMI data and extract the unique observation names,
and observations and generate the subject and observation ontology list, subject attributes,
visit observations, and subject summary files from the file. If there are any transformations
that need to be performed on the data, they are performed here. For instance the calculation
of UPDRS Totals, Semantic Fluency Totals, etc. 
"""

import argparse
import re
import sys
import pandas as pd
import pprint

study_map = {}
patient_map = {}
subject_attr_map = {}
project_id = 1
pp = pprint.PrettyPrinter(indent=4)

def main():
    parser = argparse.ArgumentParser( description='Put a description of your script here')
    parser.add_argument('-i', '--input_file', type=str, required=True, help='Path to an input file to be read' )
    parser.add_argument('-o', '--output_file_prefix', type=str, required=True, help='Prefix to use for all the output files that will be generated' )
    args = parser.parse_args()

    # Read the input as a pandas dataframe
    df = pd.read_csv(args.input_file, sep = "\t")

    # Get a list of unique items needed for processing including patient IDs, study groups, items,
    # and categories
    patient_ids = df.patient_id.unique()
    categories = df.category.unique()
    items = df.item.unique()
    scales = df.scale.unique()

    # Get the subset of columns to create the observation ontology items
    obs_ont_df = df.loc[:, ['category', 'scale']]
    obs_ont_df = obs_ont_df.drop_duplicates()
    pp.pprint(obs_ont_df)

""" 
    for row_index,row in df.iterrows():
        print (row_index,row) """

"""
    # Open the file an iterate over the list
    with open(args.input_file) as ifh:
        line = ifh.readline() # Ignore header line

        # Process the remaining lines
        for line in ifh:
            line = line.rstrip()
            # from ppmi_derived_visits.tsv
            subject_num, sex, study_group, race, birth_date, gene_category, disease_status, event_date, score, scale, event, item, category = re.split("\t", line)

            # event values are:
            print("Patient ID: {} event date {} measure {} value {}".format(subject_num, event_date, item, score))
"""


if __name__ == '__main__':
    main()
