from . import db

class SubjectAttribute(db.Model):
    __tablename__ = "subject_attribute"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    subject_ontology_id = db.Column(db.Integer, db.ForeignKey("subject_ontology.id"))
    value = db.Column(db.VARCHAR, nullable=False)

    subject = db.relationship("Subject", back_populates="attributes")
    ontology = db.relationship("SubjectOntology")

    def __init__(self,  subject_id, subject_ontology_id, value):
        self.subject_id = subject_id
        self.subject_ontology_id = subject_ontology_id
        self.value = value

    @classmethod
    def get_all_subject_attributes(cls):
        """Get all subject attributes.

        Returns:
            All subject attributes.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, subject_attribute_id):
        """Find subject attribute by id.

        Args:
            id: Subject attribute ID.

        Returns:
           Subject attribute.
        """
        return cls.query.filter_by(id=subject_attribute_id).first()

    @classmethod
    def find_by_subject_id(cls, subject_id):
        """Find all attributes by subject id.

        Args:
            id: Subject's ID.

        Returns:
            The attributes for a subject.
        """
        return cls.query.filter_by(subject_id=subject_id).all()

    @classmethod
    def find_by_subject_ontology_id(cls, subject_ontology_id):
        """Find all attributes by subject ontology id.

        Args:
          subject_ontology_id: Subject ontology ID

        Returns:
            All attributes with subject ontology id.
        """
        return cls.query.filter_by(subject_ontology_id=subject_ontology_id).all()

    def save_to_db(self):
        """Save to database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Return attributes as a dict.

        This easily allows for serializing the object and
        sending over http.
        """
        return dict(
          id=self.id,
          subject_id=self.subject_id,
          subject_ontology_id=self.subject_ontology_id,
          value=self.value,
          ontology=self.ontology.to_dict()
        )
