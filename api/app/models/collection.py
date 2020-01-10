from . import db
from . import Subject, ObservationOntology
from .cohort import Cohort
import decimal
import enum
from sqlalchemy.sql import text
import pandas as pd
import time

class InstantiationType(enum.Enum):
    static = "static"
    dynamic = "dynamic"


class Collection(db.Model):
    __tablename__ = "collection"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    label = db.Column(db.VARCHAR, nullable=False)
    date_generated = db.Column(db.TIMESTAMP)
    is_public = db.Column(db.SMALLINT, default=0)
    instantiation_type = db.Column(db.Enum(InstantiationType))
    last_modified = db.Column(db.TIMESTAMP)

    studies = db.relationship(
        "CollectionStudy",
        lazy="select",
        cascade="all, delete-orphan")
    observation_variables = db.relationship(
        "CollectionObservationVariable",
        lazy="select",
        cascade="all, delete-orphan")
    subject_variables = db.relationship(
        "CollectionSubjectVariable",
        lazy="select",
        cascade="all, delete-orphan")

    # TODO SUBJECT VARIABLES

    def __init__(self, user_id, label, is_public, instantiation_type):
        self.user_id = user_id
        self.label = label
        self.is_public = is_public
        self.instantiation_type = instantiation_type

    @classmethod
    def get_all_collections(cls):
        """Get all collections.

        Returns:
            All collections.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, collection_id):
        """Find collection by its id.

        Args:
            collection_id: Collection's ID.

        Returns:
            If exists, the collection.
        """
        return cls.query.filter_by(id=collection_id).first()

    @classmethod
    def find_all_by_user_id(cls, user_id):
        """Find all collections for user.

        Args:
            user_id: User's ID.

        Returns:
            If exists, the collections.
        """
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_all_public(cls):
        """Find all public collections.

        Args:

        Returns:
            If exists, the collections.
        """
        # include only public collections not owned by the current user
        return cls.query.filter(Collection.is_public==1)
    
    def contains_observation(self, observation_ontology_id):
        """Check if collection contains observation variable."""
        observation_ids = [
            observation_var.observation_ontology_id
            for observation_var in self.observation_variables
        ]
        return observation_ontology_id in observation_ids

    def compute_roc_across_visits_for_scale(self, observation_ontology_id):
        """TODO"""
        connection = db.engine.connect()
        study_ids = [study.study_id for study in self.studies]

        query = text("""
            SELECT s.id as subject_id,
                v.event_date as event_date,
                o.value as total
            FROM study
            JOIN subject s ON study.id = s.study_id
            JOIN  subject_visit v ON s.id = v.subject_id
            JOIN observation o ON v.id = o.subject_visit_id
            JOIN observation_ontology oo ON o.observation_ontology_id = oo.id
            WHERE study.id in (:ids) and o.observation_ontology_id in (
                SELECT id
                FROM observation_ontology
                WHERE parent_id = :parent_id
            )
            GROUP BY s.id, v.event_date
            ORDER BY total
        """)

        result_proxy = connection.execute(
            query,
            ids=','.join(str(study_id) for study_id in study_ids),
            parent_id=observation_ontology_id) \
            .fetchall()

        result = [dict(row) for row in result_proxy]

        df = pd.DataFrame(result) \
            .pivot(index='event_date', columns='subject_id', values='total')

        subject_rocs = []
        for subject_id in df.columns:
            # after pivoting there can be a lot of NA values
            # for dates that patients did not have measurements recorded
            subject_series = df[subject_id].dropna()

            # http://www.andrewshamlet.net/2017/07/07/python-tutorial-roc/
            # Calculate ROC
            n = len(subject_series)
            M = subject_series.diff(n-1)
            N = subject_series.shift(n-1)
            ROC = (M / N) * 100



        connection.close()
        return result

    def get_data_for_cohort_manager(self):
        """Get all the data from a collection that a cohort manager needs to draw charts.

        Returns
            Pandas dataframe of observation data need to draw charts.
        """

        connection = db.engine.connect()
        study_ids = [study.study_id for study in self.studies]
        # Get all subjects that are part of the studies included in
        # the collection.
        all_subjects = Subject.find_all_by_study_ids(study_ids, load_atts=True)
        subject_variable_ids = [subject_var.id for subject_var in self.subject_variables]
        obs_ids = [obs_var.ontology.id for obs_var in self.observation_variables]

        # Query for getting observation totals for patients across all
        # their visits. Note that the observations are sorted by event
        # date and visit_num, with the latter used to order multiple
        # visits on the same day.
        query_for_totals = text("""
          SELECT
              sv.subject_id as subject_id, oo.id as observation_ontology_id,
              sv.event_date, sv.visit_num, CAST(o.value AS DECIMAL) as total
          FROM subject s, subject_visit sv, observation o, observation_ontology oo
          WHERE s.study_id in :study_ids
          AND s.id = sv.subject_id
          AND sv.id = o.subject_visit_id
          AND oo.id = o.observation_ontology_id
          AND o.observation_ontology_id in :ids
          ORDER BY subject_id, observation_ontology_id, event_date, sv.visit_num
        """)

        result_proxy = connection.execute(
            query_for_totals,
            study_ids=study_ids,
            ids=obs_ids).fetchall()

        # group by subject_id, obs_id
        last_subj_id = None
        last_obs_id = None
        group_rows = []
        observations = []
        subject_observations = {}
        
        # process a set of rows grouped by subject_id, observation_ontology_id
        def process_group(subject_id, obs_id):
            if (last_subj_id is None):
                return

            # skip subjects with only one measurement/visit
            n = len(group_rows)
            if (n <= 1):
                return

            # note - using first visit on first day as "first_vist" and last visit on last day as "last_visit"
            first_date = group_rows[0]['event_date']
            last_date = group_rows[-1]['event_date']

            # http://www.andrewshamlet.net/2017/07/07/python-tutorial-roc/
            N = group_rows[0]['total']
            M = group_rows[-1]['total'] - N
            
            # normalize by duration in years
            n_years = last_date.year - first_date.year
            if n_years <= 0:
                n_years = 1

            roc = None

            # rate of change may be undefined if N = 0
            try:
                roc = ((M / N) * 100) / n_years # / 365.25)
            except decimal.InvalidOperation:
                pass
            except decimal.DivisionByZero:
                pass

            observations.append(
                dict(
                    subject_id=subject_id,
                    observation=obs_id,
                    roc=roc,
                    change=M,
                    min=group_rows[0]['total'],
                    max=group_rows[-1]['total'],
                ))

            # track observations per subject
            if subject_id not in subject_observations:
                subject_observations[subject_id] = {}
            if obs_id not in subject_observations[subject_id]:
                subject_observations[subject_id][obs_id] = True

        start_time = time.time()
                
        # read query result, group by subject_id, observation_ontology_id
        all_rows = []
        for row in result_proxy:
            rd = dict(row)
            if last_subj_id != rd['subject_id'] or last_obs_id != rd['observation_ontology_id']:
                process_group(last_subj_id, last_obs_id)
                group_rows = []

            group_rows.append(rd)
            all_rows.append(rd)
            last_subj_id = rd['subject_id']
            last_obs_id = rd['observation_ontology_id']

        process_group(last_subj_id, last_obs_id)

        # filter subjects to those with observations for all requested observation variables
        n_observation_ids = len(self.observation_variables)
        filtered_subjects = []
        for subj in all_subjects:
            subj_id = subj.to_dict()['id']
            if subj_id in subject_observations:
                obs_ids = subject_observations[subj_id]
                if len(list(obs_ids.keys())) >= n_observation_ids:
                    filtered_subjects.append(subj)

        if len(filtered_subjects) == 0:
            return { 'data': pd.DataFrame(), 'raw_data': pd.DataFrame() }

        # Because subject's attributes are in an EAV
        # table, using our model's to_dict() method to collapse these
        # into columns and join this table with our observation data
        # is easiest.
        subjects_df = pd.DataFrame([
            subject.to_dict(include_attributes=True, include_study=True)
            for subject in filtered_subjects
        ]).set_index('id')

        # Convert to datetime
        for date_col in ["Birthdate", "Enroll Date", "Diagnosis Date"]:
            if date_col in subjects_df.columns:
                subjects_df[date_col] = pd.to_datetime(subjects_df[date_col])
            
        result = pd.merge(pd.DataFrame(observations), subjects_df, left_on='subject_id', right_on='id')
        result_df = pd.DataFrame(all_rows)
        result_df['event_date'] = pd.to_datetime(result_df['event_date'])

        # set 'event_day' to time in days relative to the earliest visit (in the whole dataset)
        dates_df = result_df.set_index('event_date')
        first_date = dates_df.index.min()

        result_df['event_day'] = result_df['event_date'] - first_date
        result_df['event_day'] = result_df['event_day'].dt.days

        return { 'data': result, 'raw_data': result_df }
        # need to some how group by subject id and observation and count the number of distinct observation and see
        # if this number matches...
        # return result.groupby(['subject_id', 'observation'])['observation'].count()

    def proof_of_concept_parcoords(self):
        """Endpoint that gets data for proof of concept for drawing parcoords."""
        # TODO: REFACTOR
        # This is very inefficient/convoluted. Really need to refactor...

        connection = db.engine.connect()
        study_ids = [study.study_id for study in self.studies]
        # Get all subjects that are part of the studies included in
        # the collection. Because subject's attributes are in an EAV
        # table, using our model's to_dict() method to collapse these
        # into columns and join this table with our observation data
        # is easiest.
        subjects_df = pd.DataFrame([
            subject.to_dict(include_attributes=True, include_study=True)
            for subject in Subject.find_all_by_study_ids(study_ids)
        ]).set_index('id')
        # Convert to datetime
        if "Birthdate" in subjects_df.columns:
            query_for_first_visit = text("""
                SELECT subject_id, min(event_date) as first_visit
                FROM subject_visit
                JOIN subject on subject.id = subject_visit.subject_id
                GROUP BY subject_id;
            """)
            result_proxy = connection.execute(query_for_first_visit)
            result = [dict(row) for row in result_proxy]
            first_visit_df = pd.DataFrame(result)
            subjects_df = pd.merge(subjects_df, first_visit_df, left_on='id', right_on='subject_id')
            subjects_df['Birthdate'] = pd.to_datetime(subjects_df['Birthdate'])
            subjects_df['first_visit'] = pd.to_datetime(subjects_df['first_visit'])
            # subjects_df['age'] = subjects_df['first_visit'] - subjects_df['Birthdate'].year
            # return subjects_df
        subject_variable_ids = [subject_var.id for subject_var in self.subject_variables]

        # Separate measures that are precomputed. Currently, a measure is precomputed
        # if there are no item measures pointing to it.
        observation_variable_ids = [obs_var.ontology.id for obs_var in self.observation_variables]
        obs_ids = []
        obs_parent_ids = []
        for obs_id in observation_variable_ids:
            result = ObservationOntology.find_by_parent_id(obs_id)
            if result:
                obs_parent_ids.append(obs_id)
            else:
                obs_ids.append(obs_id)

        # Query for getting observation totals for patients across all
        # their visits.
        if obs_parent_ids:
            query = text("""
                SELECT
                    s.id as subject_id, oo.parent_id as observation_ontology_id,
                    v.event_date, v.visit_event, v.visit_num, o.value as total
                FROM study
                JOIN subject s ON study.id = s.study_id
                JOIN  subject_visit v ON s.id = v.subject_id
                JOIN observation o ON v.id = o.subject_visit_id
                JOIN observation_ontology oo ON o.observation_ontology_id = oo.id
                WHERE study.id in :study_ids and o.observation_ontology_id in (
                    SELECT id
                    FROM observation_ontology
                    WHERE parent_id in :parent_ids
                )
                GROUP BY study.id, s.id, v.event_date, v.visit_event, v.visit_num, oo.parent_id
                ORDER BY study_id, subject_id, observation_ontology_id, event_date, total
            """)
            result_proxy = connection.execute(
                query,
                study_ids=study_ids,
                parent_ids=obs_parent_ids) \
                .fetchall()
            result = [dict(row) for row in result_proxy]
            result_df = pd.DataFrame(result)

        if obs_ids:
            # Now query for precomputed
            query_for_precomputed_totals = text("""
                SELECT
                    s.id as subject_id, oo.id as observation_ontology_id,
                    v.event_date, v.visit_event, v.visit_num, o.value as total
                FROM study
                JOIN subject s ON study.id = s.study_id
                JOIN  subject_visit v ON s.id = v.subject_id
                JOIN observation o ON v.id = o.subject_visit_id
                JOIN observation_ontology oo ON o.observation_ontology_id = oo.id
                WHERE study.id in :study_ids and o.observation_ontology_id in :ids
                ORDER BY study_id, subject_id, observation_ontology_id, event_date, total
            """)
            result_proxy_for_precompute_totals = connection.execute(
                query_for_precomputed_totals,
                study_ids=study_ids,
                ids=obs_ids) \
                .fetchall()
            result_for_precompute_totals = [dict(row) for row in result_proxy_for_precompute_totals]
            result_df_for_precompute_totals = pd.DataFrame(result_for_precompute_totals)

        if obs_parent_ids and obs_ids:
            result_df = pd.concat([result_df, result_df_for_precompute_totals])
        elif not obs_parent_ids and obs_ids:
            result_df = result_df_for_precompute_totals

        # Compute ROC for each patient and each scale from their first and last visit
        observations = []
        for (subject_id, obs_id), df_shallow in result_df.groupby(['subject_id', 'observation_ontology_id']):
            df = df_shallow.copy(deep=True)
            totals = df.set_index('event_date')['total']
            first_date = totals.index.min()
            last_date = totals.index.max()

            # skip subjects with only one measurement/visit
            if (len(totals) == 1):
                continue

            # http://www.andrewshamlet.net/2017/07/07/python-tutorial-roc/
            n = len(totals)
            M = totals.diff(n-1)
            N = totals.shift(n-1)
            # normalize by both minimum visit and duration
            roc = ((M / N) * 100) / ((last_date.year - first_date.year)) # / 365.25)
            change = totals[-1] - totals[0]

            visit_totals = df[["visit_event", "total"]].set_index("visit_event")

            # df['roc'] = roc.values[-1]
            # df['change'] = change
            # df['min'] = totals.loc[first_date]
            # df['min'] = totals.loc[last_date]

            record = dict(
                    subject_id=subject_id,
                    observation=obs_id,
                    roc=roc.values[-1],
                    change=change,
                    min=totals.loc[first_date],
                    max=totals.loc[last_date],
                    **visit_totals["total"].to_dict(),
                )
            new_df = pd.merge(subjects_df, pd.DataFrame([record]), right_on='subject_id', left_on='subject_id')
            # for idx, v in visit_totals.iterrows():
            #     total = v["total"]
            #     event = v["visit_event"]
            #     record[event] = total
            observations.extend(new_df.to_dict('records'))

        return observations
        # return pd.merge(subjects_df, pd.DataFrame(observations), right_on='subject_id', left_on='subject_id')

    def save_to_db(self):
        """Save collection to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """Delete collection from the database."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self,
                include_studies=False,
                include_queries=False,
                include_variables=False,
                include_cohort_counts=False,
                # for a public Collection, the cohort user_id may differ from the Collection user_id
                cohort_user_id=None):
        """Return attributes as a dict.

        This easily allows for serializing the collection object and
        sending over http.
        """
        collection = dict(
            id=self.id,
            user_id=self.user_id,
            label=self.label,
            date_generated=self.date_generated,
            is_public=self.is_public,
        )

        if include_studies:
            collection['studies'] = [study.to_dict(
                include_study=True) for study in self.studies]

        if include_variables:
            collection['observation_variables'] = sorted([var.to_dict() for var in self.observation_variables], key=lambda x: x['ontology']['label'])
            collection['subject_variables'] = sorted([var.to_dict() for var in self.subject_variables], key=lambda x: x['ontology']['label'])

        if include_queries:
            # TODO
            pass

        if include_cohort_counts:
            all_cohorts = Cohort.find_all_by_collection_id(self.id)
            if (cohort_user_id is None):
                cohort_user_id = self.user_id
            user_cohorts = [c for c in all_cohorts if c.user_id == cohort_user_id]
            collection['num_cohorts'] = len(user_cohorts)
        
        return collection
