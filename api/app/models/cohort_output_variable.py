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

    observation_ontology = db.relationship(
        "ObservationOntology",
        lazy="select"
    )
    subject_ontology = db.relationship(
        "SubjectOntology",
        lazy="select"
    )
    study = db.relationship(
        "Study",
        lazy="select"
    )

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
            # dimension_label = str(self.dimension_label)
        )

        # Hack around ObservationDimension not being JSON serializable and will want to clean this up.
        if self.dimension_label is ObservationDimension.left_y_axis:
            output_variable['dimension_label']  = "left_y_axis"
        elif self.dimension_label is ObservationDimension.right_y_axis:
            output_variable['dimension_label']  = "right_y_axis"
        elif self.dimension_label is ObservationDimension.change:
            output_variable['dimension_label']  = "change"
        elif self.dimension_label is ObservationDimension.roc:
            output_variable['dimension_label']  = "roc"

        if self.dimension_label is None:
            output_variable['is_longitudinal'] = False
        else:
            output_variable['is_longitudinal'] = True
            
        if self.observation_ontology_id:
            output_variable['observation_ontology'] = self.observation_ontology.to_dict(include_parent=True)
        if self.subject_ontology_id:
            output_variable['subject_ontology'] = self.subject_ontology.to_dict(include_parent=True)
        if self.study_id:
            output_variable['study'] = self.study.to_dict()

        return output_variable
