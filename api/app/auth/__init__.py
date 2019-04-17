from flask import Blueprint
from flask_jwt_extended import JWTManager

jwt = JWTManager()

# Create and register auth blueprint. This blue print
# is responsible for authentication routes under /auth/
auth = Blueprint("auth", __name__)

# Import utils down here to avoid circular imports of auth
from .utils import create_tokens, custom_user_loader_error, user_loader_callback
# Import routes in order to register auth endpoints
import app.auth.routes
