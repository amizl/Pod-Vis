from . import db

class CollectionStudy(db.Model):
    __tablename__ = "collection_study"

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    study_id = db.Column(db.Integer, db.ForeignKey("study.id"))

    def __init__(self, collection_id, study_id):
        self.collection_id = collection_id
        self.study_id = study_id

    @classmethod
    def get_all_collection_studies(cls):
        """Get all collection studies.

        Returns:
            All collection studies.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, collection_study_id):
        """Find collection study by its id.

        Args:
            id: Collection Study's ID.

        Returns:
            If exists, the collection study.
        """
        return cls.query.filter_by(id=collection_study_id).first()

    @classmethod
    def find_by_collection_id(cls, collection_id):
        """Find all studies in a collection by collection_id.

        Args:
            id: Collection's ID.

        Returns:
            If exists, the collection study.
        """
        return cls.query.filter_by(collection_id=collection_id).all()

    @classmethod
    def find_by_study_id(cls, study_id):
        """Find all collections a study belong by its id.

        Args:
            study_id: Study ID

        Returns:
            All collections that include the study.
        """
        return cls.query.filter_by(study_id=study_id).all()

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
          collection_id=self.collection_id,
          study_id=self.study_id
        )