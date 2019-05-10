from . import db
import pandas as pd

class Subject(db.Model):
    __tablename__ = "subject"

    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer, db.ForeignKey("study.id"))
    subject_num = db.Column(db.Integer)

    study = db.relationship("Study", back_populates="subjects", lazy='select')
    attributes = db.relationship("SubjectAttribute", back_populates="subject", lazy="select")
    subject_visits = db.relationship("SubjectVisit", back_populates="subject", lazy="select")

    def __init__(self, study_id, subject_num):
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
    def find_by_id(cls, subject_id):
        """Find subject by its id.

        Args:
            subject_id: Subject's ID.

        Returns:
            If exists, the subject.
        """
        return cls.query.filter_by(id=subject_id).first()

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
    def find_first_by_study_id(cls, study_id):
        """Find the first subject in a study.

        Args:
            study_id: The study id that the subjects belong.

        Returns:
            The first subject in a study.
        """
        return cls.query.filter_by(study_id=study_id).first()

    @classmethod
    def count(cls, study_id, group_by):
        """Aggregate count on subjects.

        Args:
            group_by: List of attributes to group on.

        Returns:
            Aggregated counts.

        Raises:
            AttributeError if attribute in group_by is not a part of the model.
        """
        subjects = cls.find_all_by_study_id(study_id)
        subjects_df = pd.DataFrame([
            subject.to_dict(include_attributes=True)
            for subject in subjects
        ])

        # Aggregate and count for each combination of groups.
        # This is similar in SQL as:
        #
        # SELECT race, sex, count(*) as count
        # FROM subject
        # GROUP BY race, sex
        # WHERE study_id = 1;
        #
        grouped_subject_counts = subjects_df.groupby(group_by) \
            .size() \
            .reset_index(name="count")

        # "records" gives us the dictionary shape we want. For example,
        # [{"race":"white", "sex":"female", "count": 50}]
        return grouped_subject_counts.to_dict("records")

    def get_attributes(self):
        """Get subject's attribute labels.


        Returns:
            List of subject's attributes.
            Example: [
                {"attribute": "race"},
                {"attribute": "sex"}
            ]
        """
        return [
            {
                "category": attribute.ontology.parent.label if attribute.ontology.parent else None,
                "scale": attribute.ontology.label,
                "id": attribute.ontology.id
            }
            for attribute in self.attributes
        ]

    def to_dict(self, include_study=False, include_visits=False, include_attributes=False, **kwargs):
        """Return attributes as a dict.

        This easily allows for serializing the object and
        sending over http.
        """
        subject = dict(
            id=self.id,
            study_id=self.study_id,
            subject_num=self.subject_num,
        )
        if include_study:
            subject["study"] = self.study.to_dict(**kwargs)

        if include_visits:
            subject["visits"] = [
                subject_visit.to_dict(**kwargs)
                for subject_visit in self.subject_visits
            ]

        if include_attributes:
            attributes = [attribute.to_dict() for attribute in self.attributes]

            for attribute in attributes:
                # Here we flatten attributes into to a property
                # of subject as if it were a column in subject
                # table
                attr_label = attribute["ontology"]["label"]
                value = attribute["value"]
                subject[attr_label] = value

        return subject
