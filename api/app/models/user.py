from . import db, bcrypt

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    institution = db.Column(db.String(120))
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, email, name, institution, password):
        self.email = email
        self.name = name
        self.institution = institution
        self.password = password # Proxied & hashed

    @classmethod
    def find_by_email(cls, email):
        """Find user by their email.

        Args:
            email: User email.

        Returns:
            If exists, the user information from the database, else None.
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_user_id(cls, id):
        """Find user by their id

        Args:
            id: Unique ID of assigned to the user.

        Returns:
            If exists, the user from the database, else None.
        """
        return cls.query.filterby(user_id=id).first()

    @property
    def password(self):
        """Proxy password's getter to stop ability to see password."""
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """Proxy password setter to hash the password using bcrypt.

        Args:
            password: User password.
        """
        self.password_hash = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        """Check password against the hashed password to authenticate user.

        Args:
            password: User password.

        Returns:
            Boolean whether or not the password hashes to the hashed password.
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    def save_to_db(self):
        """Save the user to the database."""
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        """Return attributes as a dict.

        This easily allows for serializing the user object and
        sending over http.
        """
        return dict(
            user_id=self.user_id,
            email=self.email,
            name=self.name,
            institution=self.institution
        )
