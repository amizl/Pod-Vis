from . import db

class SubjectOntology(db.Model):
    __tablename__ = "subject_ontology"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("subject_ontology.id"))
    label = db.Column(db.VARCHAR, nullable=False)

    def __init__(self,  parent_id, label):
        self.parent_id = parent_id
        self.label= label

    @classmethod
    def get_all_subject_ontology(cls):
        """Get all subject ontology.

        Returns:
            All subject ontology.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, subject_ontology_id):
        """Find subject ontology by id.

        Args:
            id: Subject ontology ID.

        Returns:
           Subject ontology.
        """
        return cls.query.filter_by(id=subject_ontology_id).first()

    def save_to_db(self):
        """Save to database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Return attributes as a dict.

        This easily allows for serializing the study object and
        sending over http.
        """
        return dict(
          id=self.id,
          parent_id=self.parent_id,
          label=self.label
        )