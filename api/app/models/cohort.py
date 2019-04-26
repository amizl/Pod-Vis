from . import db
import enum


class InstantiationType(enum.Enum):
    static = "static"
    dynamic = "dynamic"

class Cohort(db.Model):
    __tablename__ = "cohort"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    label = db.Column(db.VARCHAR, nullable=False)
    instantiation_type = db.Column(db.Enum(InstantiationType))
    last_modified = db.Column(db.TIMESTAMP)

    subjects = db.relationship(
        "CohortSubject",
        lazy="select",
        cascade="all, delete-orphan")

    def __init__(self, user_id, label,instantiation_type):
        self.user_id = user_id
        self.label = label
        self.instantiation_type = instantiation_type

    @classmethod
    def get_all_collections(cls):
        """Get all cohorts.

        Returns:
            All cohorts.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, cohort_id):
        """Find cohort by its id.

        Args:
            cohort_id: Cohort's ID.

        Returns:
            If exists, the cohort.
        """
        return cls.query.filter_by(id=cohort_id).first()

    @classmethod
    def find_all_by_user_id(cls, user_id):
        """Find all cohorts for user.

        Args:
            user_id: User's ID.

        Returns:
            If exists, the cohorts.
        """
        return cls.query.filter_by(user_id=user_id).all()

    def save_to_db(self):
        """Save cohort to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """Delete cohort from the database."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self, include_subjects=False):
        """Return attributes as a dict.

        This easily allows for serializing the cohort object and
        sending over http.
        """
        cohort = dict(
            id=self.id,
            user_id=self.user_id,
            label=self.label,
            # instantiation_type=str(self.instantiation_type)
        )

        if include_subjects:
            cohort['subjects'] = [
                subject.to_dict()
                for subject in self.subjects
            ]

        return cohort
