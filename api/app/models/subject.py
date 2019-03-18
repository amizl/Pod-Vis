from . import db
import pandas as pd

class Subject(db.Model):
    __tablename__ = "subject"

    id = db.Column(db.Integer, primary_key=True)
    # sex = db.Column(db.String(10))
    # race = db.Column(db.String(45))
    # birth_date = db.Column(db.Date)
    study_id = db.Column(db.Integer, db.ForeignKey("study.id"))
    subject_num = db.Column(db.Integer)

    study = db.relationship("Study", back_populates="subjects", lazy='select')
    attributes = db.relationship("SubjectAttribute", back_populates="subject", lazy="select")
    # subject_visits = db.relationship("SubjectVisits")

    def __init__(self, sex, race, birth_date, study_id, subject_num):
        # self.sex = sex
        # self.race = race
        # self.birth_date = birth_date
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

        df = pd.DataFrame([
            subject.to_dict(include_attributes=True)
            for subject in subjects
        ])

        # Aggregate and count for each combination of groups.
        # This is similar in SQL as:
        #
        # SELECT race, sex count(*) as count
        # FROM subject
        # GROUP BY race, sex
        # WHERE study_id = 10;
        #
        # The size() returns a series, so we revert back to
        # a dataframe and change its value column, 0, to count.
        df = df.groupby(group_by) \
            .size() \
            .reset_index(name="count") \

        # "records" gives us the dictionary shape we need. For example,
        # [{"race":"white", "sex":"female", "count": 50}]
        return df.to_dict("records")

        # group_attributes = [getattr(cls, group) for group in group_by]
        # return cls.query.filter_by(study_id=study_id) \
        #     .with_entities(*group_attributes, db.func.count().label("count")) \
        #     .group_by(*group_attributes) \
        #     .all()

    def to_dict(self, include_study=False, include_attributes=False, **kwargs):
        """Return attributes as a dict.

        This easily allows for serializing the study object and
        sending over http.
        """
        subject = dict(
            id=self.id,
            # sex=self.sex,
            # race=self.race,
            # birth_date=self.birth_date,
            study_id=self.study_id,
            subject_num=self.subject_num,
        )
        if include_study:
            subject["study"] = self.study.to_dict(**kwargs)

        if include_attributes:
            attributes = [attribute.to_dict() for attribute in self.attributes]

            for attribute in attributes:
                # Here we flatten attributes into to a property
                # of subject as if it were a column in subject
                # table
                attr_label = attribute["ontology"]["label"]
                value = attribute["value"]
                subject[attr_label] = value

            # subject["attributes"] = [
            #     attribute.to_dict()
            #     for attribute in self.attributes
            # ]

        return subject

        # "subjects": [
        # {
        #     "attributes": [
        #         {
        #             "id": 1,
        #             "ontology": {
        #                 "id": 1,
        #                 "label": "sex",
        #                 "parent_id": null
        #             },
        #             "subject_id": 1,
        #             "subject_ontology_id": 1,
        #             "value": "female"
        #         },
        #         {
        #             "id": 2,
        #             "ontology": {
        #                 "id": 2,
        #                 "label": "race",
        #                 "parent_id": null
        #             },
        #             "subject_id": 1,
        #             "subject_ontology_id": 2,
        #             "value": "white"
        #         }
        #     ],
        #     "id": 1,
        #     "study_id": 1,
        #     "subject_num": "3000"
        # },