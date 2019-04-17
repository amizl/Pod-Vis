from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jti
)
from .exceptions import AuthFailure
from . import jwt
from .. import models
from flask import jsonify

def create_tokens(identity):
    """Create access and refresh tokens.

    Args:
        identity: The key to use as an identity when creating tokens. In our
            case this is the User model's user_id.

    Returns:
        Dict with access and refresh tokens.
    """
    access_token = create_access_token(identity=identity, fresh=True)
    access_jti = get_jti(encoded_token=access_token)

    refresh_token = create_refresh_token(identity=identity)
    refresh_jti = get_jti(encoded_token=refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}


# This function is called whenever a protected endpoint is accessed,
# and returns an object based on the tokens identity.
# This is called after the token is verified.
@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    user = models.User.find_by_id(identity)
    return user if user else None

# Override the error returned to the user if the
# user_loader_callback returns None.
@jwt.user_loader_error_loader
def custom_user_loader_error(identity):
    raise AuthFailure(f"No user was found by ID: {identity}.")
