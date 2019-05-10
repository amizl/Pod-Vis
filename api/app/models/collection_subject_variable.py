from . import db

class CollectionSubjectVariable(db.Model):
    __tablename__ = "collection_subject_variable"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    subject_ontology_id = db.Column(db.Integer, db.ForeignKey("subject_ontology.id"))

    def __init__(self, collection_id, subject_ontology_id):
        self.collection_id = collection_id
        self.subject_ontology_id = subject_ontology_id

    @classmethod
    def get_all_subject_variables(cls):
        """Get all subject variables.

        Returns:
            All subject variables within collection.
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
          subject_ontology_id=self.subject_ontology_id
        )
