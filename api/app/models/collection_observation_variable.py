from . import db
# TODO:
# Observation_scale should be a foreign key to an
# observation ontology.

class CollectionObservationVariable(db.Model):
    __tablename__ = "collection_observation_variable"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    observation_scale = db.Column(db.VARCHAR, nullable=False)

    def __init__(self, collection_id, observation_scale):
        self.collection_id = collection_id
        self.observation_scale = observation_scale

    @classmethod
    def get_all_observation_variables(cls):
        """Get all variables (outcome measures / scales).

        Returns:
            All collection variables.
        """
        return cls.query.all()

    @classmethod
    def find_by_collection_id(cls, collection_id):
        """Find all variables in a collection by collection_id.

        Args:
            collection_id: Collection's ID.

        Returns:
            Collection observation variables.
        """
        return cls.query.filter_by(collection_id=collection_id).all()

    def save_to_db(self):
        """Save the user to the database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Return attributes as a dict.

        This easily allows for serializing the object and
        sending over http.
        """
        return dict(
          id=self.id,
          collection_id=self.collection_id,
          observation_scale=self.observation_scale
        )
