from . import db

class DatasetAdded(db.Model):
    __tablename__ = 'dataset_added'

    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    study_id = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, user_id, study_id):
        self.user_id = user_id
        self.study_id = study_id

    @classmethod
    def get_all_datasets_added(cls):
        """Get all datastes added to profile.

        Returns:
            All datasets added to profile.
        """
        return cls.query.all()

    @classmethod
    def find_all_by_user_id(cls, user_id):
        """Find all datasets by user's id.

        Args:
            user_id: The user's ID.

        Returns:
            All datasets the user added to their profile.
        """
        return cls.query.filter_by(user_id=user_id).all()

    def save_to_db(self):
        """Save to the database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Convert model to dictionary.

        This easily allows for serializing the object and sending over http.

        Returns:
          Dictionary of the model's attributes.
        """
        return dict(
            user_id=self.user_id,
            study_id=self.study_id
        )
