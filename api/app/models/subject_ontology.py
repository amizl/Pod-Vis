from . import db
import enum

class DataCategory(enum.Enum):
    Categorical = "Categorical"
    Ordinal = "Ordinal"
    Continuous = "Continuous"

class ValueType(enum.Enum):
    int = "int"
    decimal = "decimal"
    char = "char"
    date = "date"

class SubjectOntology(db.Model):
    __tablename__ = "subject_ontology"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("subject_ontology.id"))
    label = db.Column(db.VARCHAR, nullable=False)
    value_type = db.Column(db.Enum(ValueType))
    data_category = db.Column(db.Enum(DataCategory))

    parent = db.relationship("SubjectOntology", remote_side=[id])

    def __init__(self,  parent_id, label, value_type, data_category):
        self.parent_id = parent_id
        self.label = label
        self.value_type = value_type
        self.data_category = data_category


    @classmethod
    def get_all_subject_ontology(cls):
        """Get all subject ontology.

        Returns:
            All subject ontology.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, subject_ontology_id):
        """Find subject ontology by id.

        Args:
            id: Subject ontology ID.

        Returns:
           Subject ontology.
        """
        return cls.query.filter_by(id=subject_ontology_id).first()

    def save_to_db(self):
        """Save to database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self, include_parent=False):
        """Return attributes as a dict.

        This easily allows for serializing the object and
        sending over http.
        """
        ontology = dict(
          id=self.id,
          parent_id=self.parent_id,
          label=self.label
        )

        if self.value_type is not None:
            ontology['value_type'] = self.value_type.value
        if self.data_category is not None:
            ontology['data_category'] = self.data_category.value

        if include_parent and self.parent:
            ontology['parent'] = self.parent.to_dict()

        return ontology
