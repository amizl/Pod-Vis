from . import db
from . import Subject, SubjectVisit, Observation, ObservationOntology
import pandas as pd
from sqlalchemy import func
from sqlalchemy.sql import text

class Study(db.Model):
    __tablename__ = "study"

    id = db.Column(db.Integer, primary_key=True)
    study_name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    longitudinal = db.Column(db.Integer, nullable=True)

    project = db.relationship("Project", back_populates="studies", lazy="select")
    subjects = db.relationship("Subject", back_populates="study", lazy="select")

    def __init__(self, study_name, description, project_id, longitudinal):
        self.study_name = study_name
        self.description = description
        self.project_id = project_id
        self.longitudinal = longitudinal

    @classmethod
    def get_all_studies(cls):
        """Get all studies.

        Returns:
            All studies.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, study_id):
        """Find study by its id.

        Args:
            id: Study's ID.

        Returns:
            If exists, the study.
        """
        return cls.query.filter_by(id=study_id).first()

    @classmethod
    def get_subject_attributes(cls, study_ids):
        """Find all attributes by study id.

        Args:
          study_ids: List of study ID

        Returns:
            All attributes in common to the specified studies.
        """
        connection = db.engine.connect()
        query = text("""
        SELECT parent.label as parent_label, so.label, so.id, so.abbreviation, so.value_type, so.data_category, so.description, COUNT(DISTINCT s.study_id) AS n_studies
        FROM subject s
        JOIN subject_attribute sa ON sa.subject_id = s.id
        JOIN subject_ontology so ON so.id = sa.subject_ontology_id
        LEFT OUTER JOIN subject_ontology parent on parent.id = so.parent_id
        WHERE s.study_id in :study_ids
        GROUP BY parent.label, so.label, so.id, so.abbreviation, so.description
        HAVING n_studies = (:n_studies)
        """)

        result_proxy = connection.execute(
            query,
            study_ids=study_ids,
            n_studies=len(study_ids)) \
            .fetchall()

        result = [{
            "category": row.parent_label if row.parent_label else None,
            "scale": row.label,
            "abbreviation": row.abbreviation,
            "value_type": row.value_type,
            "data_category": row.data_category,
            "description": row.description,
            "id": row.id,
        } for row in result_proxy]

        connection.close()
        return result
    
    @classmethod
    def get_subject_variables(cls, study_ids):
        """Retrieve all subjects, showing which variables have first+last for each.

        Args:
            id: List of study IDs.

        Returns:
            All subjects in the named studies.

        """                

        # retrieve studies, index by id
        studies = [cls.find_by_id(study_id) for study_id in study_ids]
        id2study= {}
        for study in studies:
            id2study[study.id] = study

        connection = db.engine.connect()

        # Based on query from collection.get_data_for_cohort_manager
        query_for_subject_obs_vars = text("""
          SELECT
              sv.subject_id as subject_id, s.study_id as study_id, oo.id as observation_ontology_id,
              sv.event_date, sv.visit_num
          FROM subject s, subject_visit sv, observation o, observation_ontology oo
          WHERE s.study_id in :study_ids
          AND s.id = sv.subject_id
          AND sv.id = o.subject_visit_id
          AND oo.id = o.observation_ontology_id
          ORDER BY subject_id, study_id, observation_ontology_id, event_date, sv.visit_num
        """)

        result_proxy = connection.execute(
            query_for_subject_obs_vars,
            study_ids=study_ids).fetchall()

        # dict mapping from subject id to dict of variables
        subject_vars = {}
        
        # group by subject_id, obs_id
        last_subj_id = None
        last_study_id = None
        last_obs_id = None
        group_rows = []
        
        # process a set of rows grouped by subject_id, observation_ontology_id
        def process_group(subject_id, study_id, obs_id):
            if (last_subj_id is None):
                return

            study = id2study[study_id]
            
            # skip subjects with only one measurement/visit, but only for longitudinal studies
            n = len(group_rows)
            if (n <= 1) and (study.longitudinal == 1):
                return

            if subject_id not in subject_vars:
                subject_vars[subject_id] = {}

            if study_id not in subject_vars[subject_id]:
                subject_vars[subject_id][study_id] = {}
                
            # this subject has at least two values for the specified observation,
            # or is part of a cross-sectional study
            subject_vars[subject_id][study_id][obs_id] = 1
            
        # read query result, group by subject_id, observation_ontology_id
        for row in result_proxy:
            rd = dict(row)
            if last_subj_id != rd['subject_id'] or last_study_id != rd['study_id'] or last_obs_id != rd['observation_ontology_id']:
                process_group(last_subj_id, last_study_id, last_obs_id)
                group_rows = []
            group_rows.append(rd)
            last_subj_id = rd['subject_id']
            last_study_id = rd['study_id']
            last_obs_id = rd['observation_ontology_id']
        process_group(last_subj_id, last_study_id, last_obs_id)

        # add in subject/demographic variables, where there is no first/last visit requirement
        query_for_subject_vars = text("""
          SELECT
              s.id as subject_id, s.study_id as study_id, so.id as subject_ontology_id
          FROM subject s, subject_attribute sa, subject_ontology so
          WHERE s.study_id in :study_ids
          AND s.id = sa.subject_id
          AND sa.subject_ontology_id = so.id
          ORDER BY subject_id, study_id, subject_ontology_id
        """)

        result_proxy = connection.execute(
            query_for_subject_vars,
            study_ids=study_ids).fetchall()

        for row in result_proxy:
            rd = dict(row)
            subj_id = rd['subject_id']
            study_id = rd['study_id']
            att_id = rd['subject_ontology_id']
            if subj_id not in subject_vars:
                subject_vars[subj_id] = {}
            if study_id not in subject_vars[subj_id]:
                subject_vars[subj_id][study_id] = {}
            subject_vars[subj_id][study_id][att_id] = 1
                
        return subject_vars

    @classmethod
    def get_subject_variable_visits(cls, study_ids):
        """Retrieve all subjects along with their visit/variable matrix

        Args:
            id: List of study IDs.

        Returns:
            All subjects in the named studies.

        """                

        # retrieve studies, index by id
        studies = [cls.find_by_id(study_id) for study_id in study_ids]
        id2study= {}
        for study in studies:
            id2study[study.id] = study

        connection = db.engine.connect()

        # Based on query from collection.get_data_for_cohort_manager
        query_for_subject_obs_vars = text("""
          SELECT
              sv.subject_id as subject_id, s.study_id as study_id, oo.id as observation_ontology_id,
              sv.event_date, sv.visit_num, sv.visit_event
          FROM subject s, subject_visit sv, observation o, observation_ontology oo
          WHERE s.study_id in :study_ids
          AND s.id = sv.subject_id
          AND sv.id = o.subject_visit_id
          AND oo.id = o.observation_ontology_id
          ORDER BY subject_id, study_id, observation_ontology_id, event_date, sv.visit_num
        """)

        result_proxy = connection.execute(
            query_for_subject_obs_vars,
            study_ids=study_ids).fetchall()

        # dict mapping from subject id to dict of variables
        subject_vars = {}

        # build indexes of unique visits by visit_event and visit_num
        visits = { 'event': {}, 'num': {} }

        def add_visits(r):
            study_id = r['study_id']
            visit_event = r['visit_event']
            visit_num = str(r['visit_num'])
            if visit_event not in visits['event']:
                visits['event'][visit_event] = { 'visit_event': visit_event, 'event_date': r['event_date'] }
            if visit_num not in visits['num']:
                visits['num'][visit_num] = { 'visit_num': visit_num, 'event_date': r['event_date'] }

        for row in result_proxy:
            rd = dict(row)
            add_visits(rd)
            subject_id = rd['subject_id']
            study_id = rd['study_id']
            visit_num = str(rd['visit_num'])
            oo_id = rd['observation_ontology_id']
            if subject_id not in subject_vars:
                subject_vars[subject_id] = {}
            if study_id not in subject_vars[subject_id]:
                subject_vars[subject_id][study_id] = {}
            if oo_id not in subject_vars[subject_id][study_id]:
                subject_vars[subject_id][study_id][oo_id] = { 'event': {}, 'num': {} }
            subject_vars[subject_id][study_id][oo_id]['event'][rd['visit_event']] = 1
            subject_vars[subject_id][study_id][oo_id]['num'][visit_num] = 1

        # convert dicts to arrays
        visit_events = list(visits['event'].values())
        visit_events.sort(key = lambda x: x['event_date'])
        visit_nums = list(visits['num'].values())
        visit_nums.sort(key = lambda x: x['visit_num'])
        visit_lists = { 'event': visit_events, 'num': visit_nums }

        # convert subject visits to bit strings
        subject_vars_bs = {}
        for subject_id in subject_vars:
            subject_vars_bs[subject_id] = {}
            for study_id in subject_vars[subject_id]:
                subject_vars_bs[subject_id][study_id] = {}
                for oo_id in subject_vars[subject_id][study_id]:
                    # visit_event
                    ve_str = ""
                    for ve in visit_lists['event']:
                        if ve['visit_event'] in subject_vars[subject_id][study_id][oo_id]['event']:
                            ve_str += "1"
                        else:
                            ve_str += "0"

                    # visit_num
                    vn_str = ""
                    for vn in visit_lists['num']:
                        if vn['visit_num'] in subject_vars[subject_id][study_id][oo_id]['num']:
                            vn_str += "1"
                        else:
                            vn_str += "0"

                    subject_vars_bs[subject_id][study_id][oo_id] = { 'event': ve_str, 'num': vn_str }
                
        # add in subject/demographic variables, where there is no first/last visit requirement
        query_for_subject_vars = text("""
          SELECT
              s.id as subject_id, s.study_id as study_id, so.id as subject_ontology_id
          FROM subject s, subject_attribute sa, subject_ontology so
          WHERE s.study_id in :study_ids
          AND s.id = sa.subject_id
          AND sa.subject_ontology_id = so.id
          ORDER BY subject_id, study_id, subject_ontology_id
        """)

        result_proxy = connection.execute(
            query_for_subject_vars,
            study_ids=study_ids).fetchall()

        for row in result_proxy:
            rd = dict(row)
            subj_id = rd['subject_id']
            study_id = rd['study_id']
            att_id = rd['subject_ontology_id']
            if subj_id not in subject_vars_bs:
                subject_vars_bs[subj_id] = {}
            if study_id not in subject_vars_bs[subj_id]:
                subject_vars_bs[subj_id][study_id] = {}
            subject_vars_bs[subj_id][study_id][att_id] = 1

        return { 'subjects': subject_vars_bs, 'visits': visit_lists }

    def get_variables(self):
        """Get all variables measured in a study."""
        get_scale_category = ObservationOntology.get_var_category_fn()
        connection = db.engine.connect()
        
        # get all variables measured in the study
        query = text("""
            SELECT distinct oo.label as scale, oo.id, oo.data_category, oo.value_type, oo.flip_axis, oo.abbreviation, oo.description
            FROM observation_ontology oo,
                 study s, 
                 subject subj, 
                 subject_visit sv, 
                 observation obs
            WHERE s.id = :study_id
              AND subj.study_id = s.id
              AND sv.subject_id = subj.id
              AND sv.id = obs.subject_visit_id
              AND obs.observation_ontology_id = oo.id
        """)

        result = [
            dict(category=get_scale_category(scale_id), scale=scale, id=scale_id, data_category=data_category,
                 value_type=value_type, flip_axis=flip_axis, abbreviation=abbreviation, description=description)
            for scale, scale_id, data_category, value_type, flip_axis, abbreviation, description in
            connection.execute(query, study_id=self.id).fetchall()
        ]

        connection.close()
        return result

    def get_observations(self):
        """Get all variables in a study.

        NOTE: DEPRECATED.

        This is equivalent to the SQL query:
            SELECT o.category, o.scale, o.value
            FROM study
            JOIN subject s ON study.id = s.study_id
            JOIN  subject_visit v ON s.id = v.subject_id
            JOIN observation o ON v.id = o.subject_visit_id
            WHERE study.id = %s;
        """
        return [
            dict(scale=scale, value=value)
            for scale, value in self.query.filter_by(id=self.id) \
                .join(Subject) \
                .join(SubjectVisit) \
                .join(Observation) \
                .join(ObservationOntology)
                .with_entities(ObservationOntology.label, Observation.value) \
                .all()
        ]

    def find_all_observations_by_id(self, observation_ontology_id):
        """Get all observations for a study."""
        # compute totals...
        connection = db.engine.connect()
        query = text("""

        """)


    def find_observation_value_counts_by_scale(self, observation):
        """Compute totals for each patient on each visit for scale."""
        connection = db.engine.connect()

        query = text("""
        SELECT DISTINCT o.value as value, COUNT(*) as count
        FROM study
        JOIN subject s ON study.id = s.study_id
        JOIN subject_visit v ON s.id = v.subject_id
        JOIN observation o ON v.id = o.subject_visit_id
        JOIN observation_ontology oo ON o.observation_ontology_id = oo.id
        WHERE study.id = :study_id and o.observation_ontology_id = :obs_id
        GROUP BY o.value
        ORDER BY value
        """)
        
        result_proxy = connection.execute(query, study_id=self.id,
                                          obs_id=observation.id).fetchall()
        result = [dict(row) for row in result_proxy]
            
        connection.close()
        return result

    def find_subject_attribute_counts_by_scale(self, scale):
        """Get all value counts for a subject attributes in a study by scale.
        """
        query = text("""
            SELECT o.value
            FROM study
            JOIN subject s ON study.id = s.study_id
            JOIN  subject_visit v ON s.id = v.subject_id
            JOIN observation o ON v.id = o.subject_visit_id
            WHERE study.id = %s and o.scale = %s;
        """)
        # query = text("""
        #     SELECT CAST(o.value AS SIGNED) as value
        #     FROM study
        #     JOIN subject s ON study.id = s.study_id
        #     JOIN  subject_visit v ON s.id = v.subject_id
        #     JOIN observation o ON v.id = o.subject_visit_id
        #     JOIN observation_ontology oo ON o.observation_ontology_id = oo.id
        #     WHERE study.id = 1 and o.observation_ontology_id in (
        #         SELECT id
        #         FROM observation_ontology
        #         WHERE parent_id = :parent_id
        #     )
        #     ORDER BY value
        # """)
        return [
            dict(value=value, count=count)
            for value, count in self.query.filter_by(id=self.id) \
                .join(Subject) \
                .join(SubjectVisit) \
                .join(Observation) \
                .with_entities(Observation.value, func.count(Observation.value).label('count')) \
                .filter(Observation.scale == scale) \
                .group_by(Observation.value) \
                .all()
        ]

    def total_scores(self):
        """TODO"""
        return [
                dict(scale=scale, total=total)
                for _, scale, total in self.query.filter_by(id=self.id) \
                    .join(Subject) \
                    .join(SubjectVisit) \
                    .join(Observation) \
                    .with_entities(Subject.id, Observation.scale, func.sum(Observation.value)) \
                    .group_by(Subject.id, Observation.scale) \
                    .all()
        ]

    def to_dict(self, include_num_subjects=False, include_subjects=False, include_project=False, **kwargs):
        """Return attributes as a dict.

        This easily allows for serializing the study object and
        sending over http.
        """

        study = dict(
            id=self.id,
            study_name=self.study_name,
            description=self.description,
            project_id=self.project_id,
            longitudinal=self.longitudinal,
        )

        if include_num_subjects:
            study['num_subjects'] = len(self.subjects)
        if include_subjects:
            study['subjects'] = [subject.to_dict(**kwargs) for subject in self.subjects]
        if include_project:
            study['project'] = self.project.to_dict()

        return study
