from . import db
import enum
from sqlalchemy import func


class ValueType(enum.Enum):
    int = "int"
    string = "string"
    date = "date"


class CollectionObservations(db.Model):
    __tablename__ = "collection_observations"

    collection_id = db.Column(db.Integer, primary_key=True)
    collection_name = db.Column(db.String)
    subject_id = db.Column(db.Integer, primary_key=True)
    study_name = db.Column(db.String, primary_key=True)
    visit_event = db.Column(db.String, primary_key=True)
    visit_num = db.Column(db.Integer)
    event_date = db.Column(db.Date)
    observation = db.Column(db.String, primary_key=True)

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

    @classmethod
    def summary_by_visit_event(cls, collection_id):
        """Find all the observations for this collection and group them by visit event and count them.

        Args:
            collection_id: Collection's ID.

        Returns:
            Collection observation counts grouped by collection, visit_event, and observation
        """


        results = db.session.query(CollectionObservations.visit_event, 
                            CollectionObservations.observation, func.count(CollectionObservations.collection_name)).group_by(CollectionObservations.visit_event, 
                                                                                                                            CollectionObservations.observation).filter_by(collection_id=collection_id).all()
        

        return results

    @classmethod
    def summary_by_visit_num(cls, collection_id):
        """Find all the observations for this collection and group them by visit num and count them.

        Args:
            collection_id: Collection's ID.

        Returns:
            Collection observation counts grouped by collection, visit_num, and observation
        """


        results = db.session.query(CollectionObservations.visit_num, 
                            CollectionObservations.observation, func.count(CollectionObservations.collection_name)).group_by(CollectionObservations.visit_num, 
                                                                                                                            CollectionObservations.observation).filter_by(collection_id=collection_id).all()
        

        return results

