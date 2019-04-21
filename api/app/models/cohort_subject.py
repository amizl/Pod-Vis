from . import db

class CohortSubject(db.Model):
    __tablename__ = "cohort_subject"

    id = db.Column(db.Integer, primary_key=True)
    cohort_id = db.Column(db.Integer, db.ForeignKey("cohort.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))

    subject = db.relationship("Subject", lazy="select")

    def __init__(self, cohort_id, subject_id):
        self.cohort_id = cohort_id
        self.subject_id = subject_id

    @classmethod
    def get_all_cohort_subjects(cls):
        """Get all cohort subjects.

        Returns:
            All cohort subjects.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, cohort_subject_id):
        """Find cohort subject by its id.

        Args:
            id: Cohort subject's ID.

        Returns:
            If exists, the cohort subject.
        """
        return cls.query.filter_by(id=cohort_subject_id).first()

    @classmethod
    def find_by_cohort_id(cls, cohort_id):
        """Find all subjects in a cohort.

        Args:
            id: Cohort's ID.

        Returns:
            The subjects in a a cohort.
        """
        return cls.query.filter_by(cohort_id=cohort_id).all()

    def save_to_db(self):
        """Save to database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self, include_subject=False):
        """Return attributes as a dict.

        This easily allows for serializing the object and
        sending over http.
        """
        cohort_subject =  dict(
          id=self.id,
          cohort_id=self.cohort_id,
          subject_id=self.subject_id
        )

        if include_subject:
            cohort_subject['subject'] = self.subject

        return cohort_subject
