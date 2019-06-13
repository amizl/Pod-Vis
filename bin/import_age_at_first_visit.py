import pandas as pd
import argparse
import getpass
import pymysql
import pymysql.cursors as cursors

class Password(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        if values is None:
            values = getpass.getpass()

        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser(description='Import MDS-UPDRS Totals into CliO-Vis database.')
parser.add_argument('-u', dest='user', help='User name')
parser.add_argument('-p', action=Password, nargs='?', dest='password', help='Enter password')
args = parser.parse_args()

db_kwargs = {
  "host": "localhost",
  "db": "cliovis",
  "cursorclass": cursors.DictCursor,
  "user": args.user,
  "password": args.password
}

connection = pymysql.connect(**db_kwargs)

try:
    with connection.cursor() as cursor:
        # TODO: Pass path as argument
        df = pd.read_csv('~/Projects/clio-vis/meeting/clio-vis/ppmi/ppmi_age_at_first_visit.tsv', sep='\t')


        cursor.execute("""
         SELECT *
         FROM subject_ontology
         WHERE label = 'Age at First Visit'
        """)
        result = cursor.fetchone()
        if not result:
            cursor.execute("""
                INSERT INTO subject_ontology (label, parent_id)
                VALUES ('Age at First Visit', 4)
            """)
            age_ontology_id = cursor.lastrowid
        else:
            age_ontology_id = result['id']

        for index, row in df.iterrows():
            # Get subject id
            cursor.execute("""
                SELECT id
                FROM subject
                WHERE subject_num = %s
            """, int(row['patient_id']))
            subject = cursor.fetchone()

            if subject:
                # Insert into observation
                try:
                    print(f"Inserting the age {row['age_at_first_visit']} for {subject['id']}")
                    cursor.execute("""
                        INSERT INTO subject_attribute (subject_id, subject_ontology_id, value, value_type)
                        VALUES (%s, %s, %s, %s)
                    """, (subject['id'], age_ontology_id, int(row['age_at_first_visit']), 'int'))
                except Exception as e:
                    print(e)

    connection.commit()
    print('Done.')
except Exception as e:
    print(e)
