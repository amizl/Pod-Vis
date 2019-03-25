from . import db

class Observation(db.Model):
    __tablename__ = "observation"

    id = db.Column(db.Integer, primary_key=True)
    subject_visit_id = db.Column(db.Integer, db.ForeignKey("subject_visit.id"))
    item = db.Column(db.VARCHAR, nullable=False)
    scale = db.Column(db.VARCHAR, nullable=False)
    value = db.Column(db.VARCHAR)
    category = db.Column(db.VARCHAR)
    item_type = db.Column(db.VARCHAR)

    subject_visit = db.relationship("SubjectVisit", back_populates="observations")

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

        This easily allows for serializing the study object and
        sending over http.
        """
        return dict(
          id=self.id,
          subject_visit_id=self.subject_visit_id,
          item=self.item,
          scale=self.scale,
          value=self.value,
          category=self.category,
          item_type=self.category
        )