from . import db
import enum
class InstantiationType(enum.Enum):
    static = "static"
    dynamic = "dynamic"

class Collection(db.Model):
    __tablename__ = "collection"

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    label = db.Column(db.VARCHAR, nullable=False)
    date_generated = db.Column(db.DATETIME)
    is_public = db.Column(db.SMALLINT, default=0)
    instantiation_type = db.Column(db.Enum(InstantiationType))

    def __init__(self, creator_id, label, date_generated, is_public, instantiation_type):
        self.creator_id = creator_id
        self.label = label
        self.date_generated = date_generated
        self.is_public = is_public
        self.instantiation_type = instantiation_type

    @classmethod
    def get_all_collections(cls):
        """Get all collections.

        Returns:
            All collections.
        """
        return cls.query.all()

    @classmethod
    def find_by_id(cls, collection_id):
        """Find collection by its id.

        Args:
            id: Collection's ID.

        Returns:
            If exists, the collection.
        """
        return cls.query.filter_by(id=collection_id).first()


    def save_to_db(self):
        """Save collection to the database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Return attributes as a dict.

        This easily allows for serializing the study object and
        sending over http.
        """
        return dict(
          id=self.id,
          creator_id=self.creator_id,
          label=self.label,
          date_generated=self.date_generated,
          is_public=self.is_public
        )