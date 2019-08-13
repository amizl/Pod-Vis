from . import db
import enum

class ObservationDimension(enum.Enum):
    left_y_axis = "left_y_axis"
    right_y_axis = "right_y_axis"
    roc = "roc"
    change = "change"

class CohortOutputVariable(db.Model):
    __tablename__ = "cohort_output_variable"

    id = db.Column(db.Integer, primary_key=True)
    cohort_id = db.Column(db.Integer, db.ForeignKey("cohort.id"))
    study_id = db.Column(db.Integer, db.ForeignKey("study.id"))
    observation_ontology_id = db.Column(db.Integer, db.ForeignKey("observation_ontology.id"))
    subject_ontology_id = db.Column(db.Integer, db.ForeignKey("subject_ontology.id"))
    dimension_label = db.Column(db.Enum(ObservationDimension))

    def __init__(self, cohort_id, study_id=None, observation_ontology_id=None, subject_ontology_id=None, dimension_label=None):
        self.cohort_id = cohort_id
        self.study_id = study_id
        self.observation_ontology_id = observation_ontology_id
        self.subject_ontology_id = subject_ontology_id
        self.dimension_label = dimension_label

    @classmethod
    def get_all_queries(cls):
        """Get all output variables.

        Returns:
            All output variable rows.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, output_variable_id):
        """Find output variable by its id.

        Args:
            output_variable_id: output variable's ID.

        Returns:
            If exists, the output variable row.
        """
        return cls.query.filter_by(id=output_variable_id).first()

    @classmethod
    def find_all_by_cohort_id(cls, cohort_id):
        """Find all queries for cohort.

        Args:
            cohort_id: cohort ID.

        Returns:
            If exists, the output variables.
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

        This easily allows for serializing the output variable object and
        sending over http.
        """

        output_variable = dict(
            id=self.id,
            cohort_id = self.cohort_id,
            study_id = self.study_id,
            observation_ontology_id = self.observation_ontology_id,
            subject_ontology_id = self.subject_ontology_id,
            observation_dimension = self.observation_dimension
            )

        return output_variable
