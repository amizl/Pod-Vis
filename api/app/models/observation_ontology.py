from . import db

class ObservationOntology(db.Model):
    __tablename__ = "observation_ontology"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("observation_ontology.id"))
    label = db.Column(db.VARCHAR, nullable=False)

    parent = db.relationship("ObservationOntology", remote_side=[id])

    def __init__(self,  parent_id, label):
        self.parent_id = parent_id
        self.label= label

    @classmethod
    def get_all_observation_ontology(cls):
        """Get all observation ontology.

        Returns:
            All observation ontology.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, observation_ontology_id):
        """Find observation ontology by id.

        Args:
            id: Observation ontology ID.

        Returns:
           Observation ontology.
        """
        return cls.query.filter_by(id=observation_ontology_id).first()

    @classmethod
    def find_by_parent_id(cls, observation_ontology_id):
        """Find observation ontology by id.

        Args:
            id: Observation ontology ID.

        Returns:
           Observation ontology.
        """
        return cls.query.filter_by(parent_id=observation_ontology_id).all()

    def save_to_db(self):
        """Save to database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self, include_parent=False):
        """Return attributes as a dict.

        This easily allows for serializing the object and
        sending over http.
        """
        ontology = dict(
          id=self.id,
          parent_id=self.parent_id,
          label=self.label
        )

        if include_parent and self.parent:
            ontology['parent'] = self.parent.to_dict()

        return ontology
