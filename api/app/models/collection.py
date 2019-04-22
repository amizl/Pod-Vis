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

    studies = db.relationship(
        "CollectionStudy",
        lazy="select",
        cascade="all, delete-orphan")
    variables = db.relationship(
        "CollectionObservationVariable",
        lazy="select",
        cascade="all, delete-orphan")

    def __init__(self, creator_id, label, is_public, instantiation_type):
        self.creator_id = creator_id
        self.label = label
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
            collection_id: Collection's ID.

        Returns:
            If exists, the collection.
        """
        return cls.query.filter_by(id=collection_id).first()

    @classmethod
    def find_all_by_user_id(cls, user_id):
        """Find all collections for user.

        Args:
            user_id: User's ID.

        Returns:
            If exists, the collections.
        """
        return cls.query.filter_by(creator_id=user_id).all()

    def save_to_db(self):
        """Save collection to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """Delete collection from the database."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self,
                include_studies=False,
                include_queries=False,
                include_variables=False):
        """Return attributes as a dict.

        This easily allows for serializing the collection object and
        sending over http.
        """
        collection = dict(
            id=self.id,
            creator_id=self.creator_id,
            label=self.label,
            date_generated=self.date_generated,
            is_public=self.is_public,
        )

        if include_studies:
            collection['studies'] = [study.to_dict(
                include_study=True) for study in self.studies]

        if include_variables:
            collection['variables'] = [var.to_dict() for var in self.variables]

        if include_queries:
            # TODO
            pass

        return collection
