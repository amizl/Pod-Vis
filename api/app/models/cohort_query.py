from . import db
import enum

class CohortQuery(db.Model):
    __tablename__ = "cohort_query"

    id = db.Column(db.Integer, primary_key=True)
    cohort_id = db.Column(db.Integer, db.ForeignKey("cohort.id"))
    observation_ontology_id = db.Column(db.Integer, db.ForeignKey("observation_ontology.id"), nullable=True)
    subject_ontology_id = db.Column(db.Integer, db.ForeignKey("subject_ontology.id"), nullable=True)
    min_value = db.Column(db.Integer, nullable=True)
    max_value = db.Column(db.Integer, nullable=True)
    value = db.Column(db.VARCHAR, nullable=True)

    subjects = db.relationship(
        "CohortSubject",
        lazy="select",
        cascade="all, delete-orphan")

    def __init__(self, cohort_id, obs_onto_id, subj_onto_id, min_value, max_value, value):
        self.cohort_id = cohort_id

        # Exactly one ontology type id must be present
        ontology_present = 0
        if obs_onto_id:
            self.observation_ontology_id = obs_onto_id
            ontology_present += 1
        if subj_onto_id:
            self.subject_ontology_id = subj_onto_id
            ontology_present += 1
        if ontology_present != 1:
            raise Exception("One of either 'observation_ontology_id' or 'subject_ontology_id' must be present.")

        # Must either have "value" field filled in, or must fill in both "min_value" and "max_value"
        if value:
            self.value = value
            if min_value or max_value:
                raise Exception("Cannot have 'value' field filled in conjunction with 'min_value' and 'max_value'.")
        else:
            if not (min_value and max_value):
                raise Exception("Both 'min_value' and 'max_value' must be present for the range.")
            self.min_value = min_value
            self.max_value = max_value

    @classmethod
    def get_all_queries(cls):
        """Get all cohort_query rows.

        Returns:
            All cohort_query rows.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, cq_id):
        """Find cohort_query by its id.

        Args:
            cq_id: query's ID.

        Returns:
            If exists, the cohort_query row.
        """
        return cls.query.filter_by(id=cq_id).first()

    @classmethod
    def find_all_by_cohort_id(cls, cohort_id):
        """Find all queries for cohort.

        Args:
            cohort_id: cohort ID.

        Returns:
            If exists, the queries.
        """
        return cls.query.filter_by(cohort_id=cohort_id).all()


    def save_to_db(self):
        """Save cohort query to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """Delete cohort query from the database."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Return attributes as a dict.

        This easily allows for serializing the cohort_query object and
        sending over http.
        """

        cq = dict(
            id=self.id,
            cohort_id=self.cohort_id,
            observation_ontology_id=self.observation_ontology_id,
            subject_ontology_id=self.subject_ontology_id,
            min_value=self.min_value,
            max_value=self.max_value,
            value=self.value,
        )

        return cq
