from flask import Blueprint
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, get_jti
)
from flask_redis import FlaskRedis

# Setup Redis connection for storing the blacklisted tokens
# (tokens are revoked when a user signs out)
revoked_token_store = FlaskRedis(decode_responses=True)

jwt = JWTManager()

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    """Check if the token has been revoked/blacklisted.

    In this simple case, we will store the tokens jti (unique identifier)
    in redis whenever we create a new token (with the revoked status being
    'false'). This function will return the revoked status of a token. If
    a token doesn't exist in this store, we don't know where it came from
    (as we are adding newly created tokens to our store with a revoked status
    of 'false'). In this case we will consider the token to be revoked, for
    safety purposes.

    Args:
        decrypted_token: Decypted token.

    Returns:
        True or false depending on status of token.
    """
    jti = decrypted_token['jti']
    entry = revoked_token_store.get(jti)
    if entry is None:
        return True
    return entry == 'true'

def create_and_register_tokens(identity):
    """Create access and refresh tokens and register them to our Redis cache.

    Args:
        identity: The key to use as an identity when creating tokens. In our
            case this is the User model's user_id.

    Returns:
        Dict with access and refresh tokens.
    """
    access_token = create_access_token(identity=identity, fresh=True)
    refresh_token = create_refresh_token(identity=identity)

    # Store the tokens in redis with a status of not currently revoked. We
    # can use the `get_jti()` method to get the unique identifier string for
    # each token. We can also set an expires time on these tokens in redis,
    # so they will get automatically removed after they expire. We will set
    # everything to be automatically removed shortly after the token expires
    access_jti = get_jti(encoded_token=access_token)
    refresh_jti = get_jti(encoded_token=refresh_token)

    from flask import current_app
    revoked_token_store.set(
        access_jti,
        'false',
        current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] * 1.2)
    revoked_token_store.set(
        refresh_jti,
        'false',
        current_app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 1.2)

    return { "access_token": access_token, "refresh_token": refresh_token }

auth = Blueprint("auth", __name__)
# Import routes in order to register auth endpoints
import app.auth.routes