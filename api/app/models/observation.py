from . import db
import enum

class ValueType(enum.Enum):
    int = "int"
    string = "string"
    date = "date"

class Observation(db.Model):
    __tablename__ = "observation"

    id = db.Column(db.Integer, primary_key=True)
    subject_visit_id = db.Column(db.Integer, db.ForeignKey("subject_visit.id"))
    observation_ontology_id = db.Column(db.Integer, db.ForeignKey("observation_ontology.id"))
    value = db.Column(db.VARCHAR)
    value_type = db.Column(db.Enum(ValueType))

    subject_visit = db.relationship("SubjectVisit", back_populates="observations")
    ontology = db.relationship("ObservationOntology")

    def __init__(self,  subject_visit_id, observation_ontology_id, value, value_type):
        self.subject_visit_id = subject_visit_id
        self.observation_ontology_id = observation_ontology_id
        self.value = value
        self.value_type = value_type

    @classmethod
    def get_all_observations(cls):
        """Get all observations.

        Returns:
            All observations.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, observation_id):
        """Find observation by id.

        Args:
            id: Subject attribute ID.

        Returns:

        """
        return cls.query.filter_by(id=observation_id).first()

    @classmethod
    def find_all_by_subject_visit_id(cls, subject_visit_id):
        """Find all observations by subject visit id
        Args:
            id: Subject visit ID.

        Returns:
            Observations for a visit.
        """
        return cls.query.filter_by(subject_visit_id=subject_visit_id).all()


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
          subject_visit_id=self.subject_visit_id,
          # TODO... join obs ont id to get label...
          observation_ontology_id=self.observation_ontology_id,
          ontology=self.ontology.to_dict(),
          value=self.value,
          value_type=self.value_type
        )
