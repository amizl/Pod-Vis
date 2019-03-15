from . import db

class CollectionQuery(db.Model):
    __tablename__ = "collection_query"

    collection_query_id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.collection_id"))
    param = db.Column(db.VARCHAR, nullable=False)
    operator = db.Column(db.VARCHAR, nullable=False)
    value = db.Column(db.VARCHAR, nullable=False)

    def __init__(self, collection_query_id, collection_id, param, operator, value):
        self.collection_query_id = collection_query_id
        self.collection_id = collection_id
        self.param = param
        self.operator = operator
        self.value = value

    @classmethod
    def get_all_collection_queries(cls):
        """Get all collection queries.

        Returns:
            All collection queres.
        """
        return cls.query.all()

    @classmethod
    def find_by_collection_query_id(cls, collection_query_id):
        """Find collection query by its id.

        Args:
            collection_query_id: Collection Query's ID.

        Returns:
            If exists, the collection query.
        """
        return cls.query.filter_by(collection_query_id=collection_query_id).first()

    @classmethod
    def find_by_collection_id(cls, collection_id):
        """Find all studies in a collection by collection_id.

        Args:
            collection_study_id: Collection's ID.

        Returns:
            If exists, the collection study.
        """
        return cls.query.filter_by(collection_id=collection_id).all()

    def to_dict(self):
        """Return attributes as a dict.

        This easily allows for serializing the study object and
        sending over http.
        """
        return dict(
          collection_query_id=self.collection_study_id,
          collection_id=self.collection_id,
          param=self.param,
          operator=self.operator,
          value=self.value
        )