from . import db

class Subject(db.Model):
    __tablename__ = "subject"

    subject_id = db.Column(db.Integer, primary_key=True)
    sex = db.Column(db.String(10))
    race = db.Column(db.String(45))
    birth_date = db.Column(db.Date)
    study_id = db.Column(db.Integer, db.ForeignKey("study.study_id"))
    subject_num = db.Column(db.Integer)

    study = db.relationship("Study", back_populates="subjects", lazy='select')
    # subject_visits = db.relationship("SubjectVisits")

    def __init__(self, subject_id, sex, race, birth_date, study_id, subject_num):
        self.subject_id = subject_id
        self.sex = sex
        self.race = race
        self.birth_date = birth_date
        self.study_id = study_id
        self.subject_num = subject_num

    @classmethod
    def get_all_subjects(cls):
        """Get all subjects.

        Returns:
            All subjects.
        """
        return cls.query.all()

    @classmethod
    def find_by_subject_id(cls, subject_id):
        """Find subject by its id.

        Args:
            subject_id: Subject's ID.

        Returns:
            If exists, the subject.
        """
        return cls.query.filter_by(subject_id=subject_id).first()

    @classmethod
    def find_all_by_study_id(cls, study_id):
        """Find all subjects by study id.

        Args:
            study_id: The study id that the subjects belong.

        Returns:
            All subjects within study.
        """
        return cls.query.filter_by(study_id=study_id).all()


    @classmethod
    def count(cls, study_id, *group_by):
        """Aggregate count on subjects.

        Args:
            group_by: Attributes to group on.

        Returns:
            Aggregated counts.

        Raises:
            AttributeError if attribute in group_by is not a part of the model.
        """
        group_attributes = [getattr(cls, group) for group in group_by]

        return cls.query.filter_by(study_id=study_id) \
            .with_entities(*group_attributes, db.func.count().label("count")) \
            .group_by(*group_attributes) \
            .all()

    def to_dict(self, include_study=False, **kwargs):
        """Return attributes as a dict.

        This easily allows for serializing the study object and
        sending over http.
        """
        subject = dict(
            subject_id=self.subject_id,
            sex=self.sex,
            race=self.race,
            birth_date=self.birth_date,
            study_id=self.study_id,
            subject_num=self.subject_num,
        )
        if include_study:
            subject["study"] = self.study.to_dict(**kwargs)

        return subject