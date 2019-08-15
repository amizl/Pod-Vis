from . import db
import enum

class ObservationDimension(enum.Enum):
    left_y_axis = "left_y_axis"
    right_y_axis = "right_y_axis"
    roc = "roc"
    change = "change"

class CohortInputVariable(db.Model):
    __tablename__ = "cohort_input_variable"

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
        """Get all input variables.

        Returns:
            All input variable rows.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, input_variable_id):
        """Find input variable by its id.

        Args:
            input_variable_id: Input variable's ID.

        Returns:
            If exists, the input variable row.
        """
        return cls.query.filter_by(id=input_variable_id).first()

    @classmethod
    def find_all_by_cohort_id(cls, cohort_id):
        """Find all queries for cohort.

        Args:
            cohort_id: cohort ID.

        Returns:
            If exists, the input variables.
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

        This easily allows for serializing the input variable object and
        sending over http.
        """

        input_variable = dict(
            id=self.id,
            cohort_id = self.cohort_id,
            study_id = self.study_id,
            observation_ontology_id = self.observation_ontology_id,
            subject_ontology_id = self.subject_ontology_id,
            # dimension_label = str(self.dimension_label)
            )

        # Hack around ObservatonDimension not being JSON serializ
        #
        if self.dimension_label is ObservationDimension.left_y_axis:
            input_variable['dimension_label']  = str(ObservationDimension.left_y_axis)
        elif self.dimension_label is ObservationDimension.right_y_axis:
            input_variable['dimension_label']  = str(ObservationDimension.right_y_axis)
        elif self.dimension_label is ObservationDimension.change:
            input_variable['dimension_label']  = str(ObservationDimension.change)
        elif self.dimension_label is ObservationDimension.roc:
            input_variable['dimension_label']  = str(ObservationDimension.roc)

        if self.observation_ontology_id:
            input_variable['observaton_ontology'] = self.observation_ontology.to_dict()
        if self.subject_ontology_id:
            input_variable['subject_ontology'] = self.subject_ontology.to_dict()
        if self.study_id:
            input_variable['study'] = self.study.to_dict()

        return input_variable
