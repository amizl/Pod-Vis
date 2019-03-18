from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jti,
    get_raw_jwt,
    jwt_refresh_token_required,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
from . import (
    auth,
    create_tokens
)
from .exceptions import AuthFailure
from .validators import validate_sign_in, validate_sign_up
from ..models import db, User

@auth.route('/signin')
@jwt_required
def is_user_token_expired():
    """Checks if user's access token is expired.

    If this method gets called, then it made it passed the jwt_required
    decorator. This means that there was an access token cookie and it is
    not expired.

    Returns:
        User information.
    """
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    if user:
        response = jsonify({
            "user": user.to_dict()
        })
        return response
    else:
        raise AuthFailure('No user by this ID was found.')

@auth.route('/signin', methods=['POST'])
@validate_sign_in
def sign_user_in():
    """Signs the user in.

    The user does not have an active session, so sign
    the user in with their credentials.

    Form Args:
        email: The user's email.
        password: The user's password.

    Returns:
        User information.
    """
    request_data = request.get_json()

    email = request_data.get('email')
    user = User.find_by_email(email)
    if user:
        pw = request_data.get('password')
        if user.verify_password(pw):
            response = jsonify({
                "user": user.to_dict()
            })
            jwt_tokens = create_tokens(user.id)
            set_access_cookies(response, jwt_tokens['access_token'])
            set_refresh_cookies(response, jwt_tokens['refresh_token'])
            return response
        else:
            raise AuthFailure('Email or password is incorrect.')
    else:
        raise AuthFailure('Email or password is incorrect.')

# Endpoint for revoking the current user's access token
@auth.route('/signout', methods=['DELETE'])
@jwt_required
def sign_user_out():
    """Sign the user out by revoking their access token.

    Revoke the user's token by removing the jwt cookies.
    """
    response = jsonify({"msg": "Access token revoked."})
    unset_jwt_cookies(response)
    return response

@auth.route('/signup', methods=['POST'])
@validate_sign_up
def sign_user_up():
    """Sign the user up.

    If the email does not currently exist in the database,
    sign the user up by creating new entry in user table.

    Returns:
        User information.
    """
    request_data = request.get_json()

    email = request_data.get('email')
    user = User.find_by_email(email)
    if not user:
        # Email doesn't exist, create new user with their info
        name = request_data.get('name')
        institution = request_data.get('institution')
        password = request_data.get('password')

        new_user = User(email, name, institution, password)
        new_user.save_to_db()

        response = jsonify({
             "user": new_user.to_dict()
        })

        jwt_tokens = create_tokens(new_user.id)
        set_access_cookies(response, jwt_tokens['access_token'])
        set_refresh_cookies(response, jwt_tokens['refresh_token'])
        return response, 201
    else:
        raise AuthFailure('User with this email already exists.')

@auth.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """Refresh the user's access token.

    Returns:
        Access token.
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    response = jsonify({"msg": "Access token refreshed."})
    set_access_cookies(response, access_token)
    return response, 201

@auth.route('/refresh', methods=['DELETE'])
@jwt_refresh_token_required
def sign_out_refresh():
    """Revoke refresh token and delete cookie."""
    response = jsonify({"msg": "Refresh token revoked."})
    unset_jwt_cookies(response)
    return response
