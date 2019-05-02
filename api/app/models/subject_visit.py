from . import db
class SubjectVisit(db.Model):
    __tablename__ = "subject_visit"

    id = db.Column(db.Integer, primary_key=True)
    visit_event = db.Column(db.VARCHAR)
    visit_num = db.Column(db.Integer)
    event_date = db.Column(db.Date)
    disease_status = db.Column(db.VARCHAR)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))

    observations = db.relationship("Observation")
    subject = db.relationship("Subject", back_populates="subject_visits", lazy='select')

    def __init__(self,  parent_id, label):
        self.parent_id = parent_id
        self.label= label

    @classmethod
    def get_all_subject_visits(cls):
        """Get all subject visits.

        Returns:
            All subject visits.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, subject_visit_id):
        """Find subject visit by id.

        Args:
            subject_vist_id: Subject visit ID.

        Returns:
           Subject vsit.
        """
        return cls.query.filter_by(id=subject_visit_id).first()

    def save_to_db(self):
        """Save to database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self, include_observations=False, **kwargs):
        """Return attributes as a dict.

        This easily allows for serializing the object and
        sending over http.
        """

        visit = dict(
          id=self.id,
          visit_event=self.visit_event,
          visit_num=self.visit_num,
          event_date=self.event_date,
          disease_status=self.disease_status,
          subject_id=self.subject_id
        )

        if include_observations:
          visit['observations'] = [observation.to_dict(**kwargs) for observation in self.observations]

        return visit