from . import db
import enum
from sqlalchemy.sql import text

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

    @classmethod
    def get_var_category_fn(cls):
        """Get function that maps variable id to variable category.

        Args:

        Returns:
           Function that maps variable id to variable category.
        """
        connection = db.engine.connect()

        # build lookup table/function to determine top-level category for each scale (observation ontology term)
        query = text("""
            SELECT distinct oo_p.id as parent_id, oo_p.label as parent_label, oo.id, oo.label
            FROM observation_ontology oo, observation_ontology oo_p
            WHERE oo.parent_id = oo_p.id
        """)

        # map each ontology term to its immediate parent
        o2p = {}
        for parent_id, parent_label, id, label in connection.execute(query).fetchall():
            if (id != parent_id):
                o2p[id] = {"id": parent_id, "label": parent_label}

        # map each ontology term to its highest level parent (i.e., category)
        def get_scale_category(id):
            parent = {'id': id}
            while parent['id'] in o2p:
                parent = o2p[parent['id']]
            if 'label' in parent:
                return parent['label']
            else:
                return None

        connection.close()
        return get_scale_category
    
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
