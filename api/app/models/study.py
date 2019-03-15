from . import db

class Study(db.Model):
    __tablename__ = "study"

    study_id = db.Column(db.Integer, primary_key=True)
    study_name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.project_id"))

    project = db.relationship("Project", back_populates="studies")
    subjects = db.relationship("Subject", back_populates="study", lazy="select")

    def __init__(self, study_id, study_name, description, project_id):
        self.study_id = study_id
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
    def find_by_study_id(cls, study_id):
        """Find study by its id.

        Args:
            study_id: Study's ID.

        Returns:
            If exists, the study.
        """
        return cls.query.filter_by(study_id=study_id).first()

    def to_dict(self, include_subjects=False, include_project=False, **kwargs):
        """Return attributes as a dict.

        This easily allows for serializing the study object and
        sending over http.
        """

        study = dict(
            study_id=self.study_id,
            study_name=self.study_name,
            description=self.description,
            project_id=self.project_id,
        )
        if include_subjects:
            study['subjects'] = [subject.to_dict(**kwargs) for subject in self.subjects]
        if include_project:
            study['project'] = self.project.to_dict()

        return study
