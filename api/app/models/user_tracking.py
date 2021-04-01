from . import db
from . import Subject, ObservationOntology
from sqlalchemy.sql import text
import sys
import time

class UserTracking(db.Model):
    __tablename__ = "user_tracking"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.TIMESTAMP)
    source_path = db.Column(db.VARCHAR, nullable=False)
    path = db.Column(db.VARCHAR, nullable=False)
    action = db.Column(db.VARCHAR, nullable=False)
    event_category = db.Column(db.VARCHAR, nullable=False)
    event_label = db.Column(db.VARCHAR, nullable=False)

    def __init__(self, user_id, source_path, path, action, event_category, event_label):
        self.user_id = user_id
        self.date = None
        self.source_path = source_path
        self.path = path
        self.action = action
        self.event_category = event_category
        self.event_label = event_label

    @classmethod
    def find_all_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        user_tracking = dict(
            id=self.id,
            user_id=self.user_id,
            date=self.date,
            source_path=self.source_path,
            path=self.path,
            action=self.action,
            event_category=self.event_category,
            event_label=self.event_label,

        )
        return user_tracking
