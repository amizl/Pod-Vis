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
        df = pd.read_csv('~/Projects/clio-vis/meeting/clio-vis/ppmi/ppmi_updrs_total.tsv', sep='\t')

        cursor.execute("""
         SELECT *
         FROM observation_ontology
         WHERE label = 'MDS-UPDRS Total (Part I-III)'
        """)
        result = cursor.fetchone()
        if not result:
            cursor.execute("""
                INSERT INTO observation_ontology (label, parent_id)
                VALUES ('MDS-UPDRS Total (Part I-III)', 105)
            """)
            total_ontology_id = cursor.lastrowid
        else:
            total_ontology_id = result['id']

        for index, row in df.iterrows():
            # Get subject id
            cursor.execute("""
                SELECT id
                FROM subject
                WHERE subject_num = %s
            """, row['patient_id'])
            subject = cursor.fetchone()

            if subject:
                # Get visit id from subject id and event ('Baseline', 'Visit 1', etc.)
                cursor.execute("""
                    SELECT id
                    FROM subject_visit
                    WHERE subject_id = %s AND visit_event = %s
                """, (subject['id'], row['event']))
                visit = cursor.fetchone()
                if visit:
                    # Insert into observation
                    print(f"Inserting {total_ontology_id}, {row['score']}, {visit['id']}, 'int', into observation...")
                    try:
                        cursor.execute("""
                            INSERT INTO observation (observation_ontology_id, value, subject_visit_id, value_type)
                            VALUES (%s, %s, %s, %s)
                        """, (total_ontology_id, row['score'], visit['id'], 'int'))
                    except Exception as e:
                        print(e)

    connection.commit()
    print('Done.')
except Exception as e:
    print(e)
