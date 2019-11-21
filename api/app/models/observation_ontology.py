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
    
class ObservationOntology(db.Model):
    __tablename__ = "observation_ontology"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("observation_ontology.id"))
    label = db.Column(db.VARCHAR, nullable=False)
    value_type = db.Column(db.Enum(ValueType))
    data_category = db.Column(db.Enum(DataCategory))
    flip_axis = db.Column(db.Integer, nullable=True)
    
    parent = db.relationship("ObservationOntology", remote_side=[id])

    def __init__(self,  parent_id, label, value_type, data_category, flip_axis):
        self.parent_id = parent_id
        self.label = label
        self.value_type = value_type
        self.data_category = data_category
        self.flip_axis = flip_axis

    @classmethod
    def get_all_observation_ontology(cls):
        """Get all observation ontology.

        Returns:
            All observation ontology.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, observation_ontology_id):
        """Find observation ontology by id.

        Args:
            id: Observation ontology ID.

        Returns:
           Observation ontology.
        """
        return cls.query.filter_by(id=observation_ontology_id).first()

    @classmethod
    def find_by_parent_id(cls, observation_ontology_id):
        """Find observation ontology by id.

        Args:
            id: Observation ontology ID.

        Returns:
           Observation ontology.
        """
        return cls.query.filter_by(parent_id=observation_ontology_id).all()

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
          label=self.label,
          flip_axis=self.flip_axis,
        )

        if self.value_type is not None:
            ontology['value_type'] = self.value_type.value
        if self.data_category is not None:
            ontology['data_category'] = self.data_category.value
        
        if include_parent and self.parent:
            ontology['parent'] = self.parent.to_dict()

        return ontology
