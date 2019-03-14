from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jti
)
from . import jwt

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
