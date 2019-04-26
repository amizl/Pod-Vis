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

    def __init__(self,  subject_visit_id, item, scale, value, category, item_type):
        self.subject_visit_id = subject_visit_id
        self.item = item
        self.scale = scale
        self.value = value
        self.category = category
        self.item_type = item_type

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
          item=self.item,
          scale=self.scale,
          value=self.value,
          category=self.category,
          item_type=self.item_type
        )
