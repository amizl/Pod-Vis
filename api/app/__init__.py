from flask import Flask
from flask_cors import CORS
from config import config
# http://flask.pocoo.org/docs/1.0/patterns/appfactories/#app-factories
def create_app(config_name):
    """Application Factory function to kickstart the Flask app

    Args:
        config_name: The configuration name ('development', 'production') for
        the application to run.

    Returns:
        The flask application object with configuration, database, and
        api blueprints (routes/endpoints) initialized.
    """
    app = Flask(__name__)
    # If we want to access API from different host.
    CORS(app)

    # Set up configuration (production, development, or testing)...
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Register database to app...
    from .models import db, bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    # use JWTs to authorize protected api endpoints
    from .auth import jwt, revoked_token_store
    jwt.init_app(app)
    revoked_token_store.init_app(app)

    # Register endpoint blueprints...
    from .api import api as api_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
