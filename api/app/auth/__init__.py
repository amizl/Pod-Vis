from flask import Blueprint
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

jwt = JWTManager()

from .utils import create_tokens

# Create and register auth blueprint. This blue print
# is responsible for authentication routes under /auth/
auth = Blueprint("auth", __name__)
# Import routes in order to register auth endpoints
import app.auth.routes
