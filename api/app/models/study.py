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

    def get_variables(self):
        """Get all variables measured in a study."""
        connection = db.engine.connect()

        # build lookup table/function to determine top-level category for each scale (observation ontology term)
        query = text("""
            SELECT distinct oo_p.id as parent_id, oo_p.label as parent_label, oo.id, oo.label
            FROM observation_ontology oo, observation_ontology oo_p
            WHERE oo.parent_id = oo_p.id
        """)

        # map each ontology term to its immediate parent
        o2p = {}
        for parent_id, parent_label, id, label in connection.execute(query).fetchall():
            if (id != parent_id):
                o2p[id] = {"id": parent_id, "label": parent_label};

        # map each ontology term to its highest level parent (i.e., category)
        def get_scale_category(id):
            parent = {'id': id}
            while parent['id'] in o2p:
                parent = o2p[parent['id']]
            return parent['label']

        # get all variables measured in the study
        query = text("""
            SELECT distinct oo.label as scale, oo.id, oo.data_category, oo.value_type, oo.flip_axis
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
            dict(category=get_scale_category(scale_id), scale=scale, id=scale_id, data_category=data_category, value_type=value_type, flip_axis=flip_axis)
            for scale, scale_id, data_category, value_type, flip_axis in
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

    def to_dict(self, include_subjects=False, include_project=False, **kwargs):
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
        if include_subjects:
            study['subjects'] = [subject.to_dict(**kwargs) for subject in self.subjects]
        if include_project:
            study['project'] = self.project.to_dict()

        return study
