from flask import Blueprint
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

# Setup Redis connection for storing the blacklisted tokens
# (tokens are revoked when a user signs out)
revoked_token_store = FlaskRedis(decode_responses=True)

jwt = JWTManager()

from .utils import (
   create_and_register_tokens, register_token, revoke_token
)

# Create and register auth blueprint. This blue print
# is responsible for authentication routes under /auth/
auth = Blueprint("auth", __name__)
# Import routes in order to register auth endpoints
import app.auth.routes
