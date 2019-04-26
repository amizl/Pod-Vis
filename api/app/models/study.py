from . import db
from . import Subject, SubjectVisit, Observation
import pandas as pd
from sqlalchemy import func

class Study(db.Model):
    __tablename__ = "study"

    id = db.Column(db.Integer, primary_key=True)
    study_name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    project = db.relationship("Project", back_populates="studies", lazy="select")
    subjects = db.relationship("Subject", back_populates="study", lazy="select")

    def __init__(self, study_name, description, project_id):
        self.study_name = study_name
        self.description = description
        self.project_id = project_id

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
        """Get all variables in a study.

        This is equivalent to the SQL query:
            SELECT DISTINCT o.category, o.scale
            FROM study
            JOIN subject s ON study.id = s.study_id
            JOIN  subject_visit v ON s.id = v.subject_id
            JOIN observation o ON v.id = o.subject_visit_id
            WHERE study.id = %s;
        """
        return [
            dict(category=category, scale=scale)
            for category, scale in self.query.filter_by(id=self.id) \
                .join(Subject) \
                .join(SubjectVisit) \
                .join(Observation) \
                .with_entities(Observation.category, Observation.scale) \
                .distinct() \
                .all()
        ]

    def get_observations(self):
        """Get all variables in a study.

        This is equivalent to the SQL query:
            SELECT o.category, o.scale, o.value
            FROM study
            JOIN subject s ON study.id = s.study_id
            JOIN  subject_visit v ON s.id = v.subject_id
            JOIN observation o ON v.id = o.subject_visit_id
            WHERE study.id = %s;
        """
        return [
            dict(category=category, scale=scale, value=value)
            for category, scale, value in self.query.filter_by(id=self.id) \
                .join(Subject) \
                .join(SubjectVisit) \
                .join(Observation) \
                .with_entities(Observation.category, Observation.scale, Observation.value) \
                .all()
        ]

    def find_observations_by_scale(self, scale):
        """Get all observations in a study by scale.

        This is equivalent to the SQL query:
            SELECT o.value
            FROM study
            JOIN subject s ON study.id = s.study_id
            JOIN  subject_visit v ON s.id = v.subject_id
            JOIN observation o ON v.id = o.subject_visit_id
            WHERE study.id = %s and o.scale = %s;
        """
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
        )
        if include_subjects:
            study['subjects'] = [subject.to_dict(**kwargs) for subject in self.subjects]
        if include_project:
            study['project'] = self.project.to_dict()

        return study
