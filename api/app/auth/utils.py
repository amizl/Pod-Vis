from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jti
)
from . import jwt

def create_tokens(identity):
    """Create access and refresh tokens and register them to our Redis store.

    Store the tokens in redis with a status of not currently revoked. We
    can use the `get_jti()` method to get the unique identifier string for
    each token. We can also set an expires time on these tokens in redis,
    so they will get automatically removed after they expire. We will set
    everything to be automatically removed shortly after the token expires

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
