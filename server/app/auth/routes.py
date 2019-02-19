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
    jwt,
    revoked_token_store,
    create_and_register_tokens,
    register_token,
    revoke_token
)
from .exceptions import AuthFailure
from ..models import db, User

@auth.route('/signin', methods=['POST'])
def sign_user_in():
    """Signs the user in and returns JWT access/refresh tokens.

    Form Args:
        email: The user's email.
        password: The user's password.

    Returns:
        User information. (TODO)
    """
    request_data = request.get_json()

    email = request_data.get('email')
    user = User.find_by_email(email)
    if user:
        pw = request_data.get('password')
        if user.verify_password(pw):
            response = jsonify({
                "message": "Successfully signed in."
            })
            # TODO respond with other user info here...

            jwt_tokens = create_and_register_tokens(user.user_id)
            set_access_cookies(response, jwt_tokens['access_token'])
            set_refresh_cookies(response, jwt_tokens['refresh_token'])

            return response
        else:
            raise AuthFailure('Password is incorrect.')
    else:
        raise AuthFailure('The username does not exist.')


# Endpoint for revoking the current user's access token
@auth.route('/signout', methods=['DELETE'])
@jwt_required
def sign_user_out():
    """Sign the user out by revoking their access token.

    Revoke the user's token by setting the JWT id in our
    redis db to "true" and then remove the jwt cookies.
    """
    jti = get_raw_jwt()['jti']
    revoke_token(jti, 'access')

    response = jsonify({"message": "Access token revoked."})
    unset_jwt_cookies(response)

    return response

@auth.route('/signup', methods=['POST'])
def sign_user_up():
    """Sign the user up.

    If the email does not currently exist in the database,
    sign the user up by creating new entry in user table.

    Returns:
        User information. (TODO)
    """
    request_data = request.get_json()

    email = request_data.get('email')
    user = User.find_by_email(email)
    if not user:
        name = request_data.get('name')
        institution = request_data.get('institution')
        password = request_data.get('password')

        new_user = User(
            email=email,
            name=name,
            institution=institution,
            password=password)
        # save new user in the database
        new_user.save_to_db()

        response = jsonify({
            "message": "Successfully signed in."
            # TODO respond with other user info here...
        })

        jwt_tokens = create_and_register_tokens(new_user.user_id)
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
    access_jti = get_jti(encoded_token=access_token)
    register_token(access_jti, "access")

    response = jsonify({"access_token": access_token})
    set_access_cookies(response, access_token)
    return response, 201

@auth.route('/refresh', methods=['DELETE'])
@jwt_refresh_token_required
def sign_out_refresh():
    """Revoke refresh token and delete cookie."""
    jti = get_raw_jwt()['jti']
    revoke_token(jti, 'refresh')

    response = jsonify({"message": "Refresh token revoked."})
    unset_jwt_cookies(response)
    return response
