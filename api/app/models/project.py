from . import db

class Project(db.Model):
    __tablename__ = "project"

    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)

    studies = db.relationship("Study", back_populates="project", lazy="select")

    def __init__(self, project_id, project_name, description):
        self.project_id = project_id
        self.project_name = project_name
        self.description = description

    @classmethod
    def get_all_projects(cls):
        """Get all projects.

        Returns:
            All projects.
        """
        return cls.query.all()

    @classmethod
    def find_by_project_id(cls, project_id):
        """Find project by its id.

        Args:
            project_id: Project's ID.

        Returns:
            If exists, the project.
        """
        return cls.query.filter_by(project_id=project_id).first()

    def to_dict(self, include_studies=False, **kwargs):
        """Convert model to dictionary.

        This easily allows for serializing the object and sending over http.

        Returns:
          Dictionary of the model's attributes.
        """
        project = dict(
            project_id=self.project_id,
            project_name=self.project_name,
            description=self.description,
        )

        if include_studies:
            project["studies"] = [study.to_dict(**kwargs) for study in self.studies]

        return project

