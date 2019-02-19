from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jti,
    get_raw_jwt,
    jwt_refresh_token_required,
    get_jwt_identity
)
from . import auth, jwt, revoked_token_store, create_and_register_tokens
from .exceptions import AuthFailure
from ..models import db, User

@auth.route('/signin', methods=['POST'])
def sign_user_in():
    """Signs the user in and returns JWT access/refresh tokens.

    Form Args:
        email: The user's email.
        password: The user's password.

    Returns:
        JWT access and refresh tokens.
    """
    request_data = request.get_json()

    email = request_data.get('email')
    user = User.find_by_email(email)
    if user:
        pw = request_data.get('password')
        if user.verify_password(pw):
            access_refresh_tokens = create_and_register_tokens(user.user_id)
            return jsonify(access_refresh_tokens)
        else:
            raise AuthFailure('Password is incorrect.')
    else:
        raise AuthFailure('The username does not exist.')


# Endpoint for revoking the current users access token
@auth.route('/signout', methods=['DELETE'])
@jwt_required
def sign_user_out():
    jti = get_raw_jwt()['jti']

    from flask import current_app
    revoked_token_store.set(
        jti,
        'true',
        current_app.config['JWT_ACCESS_EXPIRES'] * 1.2)

    return jsonify({"message": "Access token revoked."}), 200

@auth.route('/signup', methods=['POST'])
def sign_up():
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
        new_user.save_to_db()

        return jsonify({'message': "Account creation successful."}), 201
    else:
        raise AuthFailure('User with this email already exists.')

# Blacklisted refresh tokens will not be able to access this endpoint
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

    from flask import current_app
    revoked_token_store.set(
        access_jti,
        'false',
        current_app.config['JWT_ACCESS_EXPIRES'] * 1.2)
    return jsonify({"access_token": access_token}), 201

# Endpoint for revoking the current users refresh token
@auth.route('/refresh-revoke', methods=['DELETE'])
@jwt_refresh_token_required
def sign_out_refresh():
    jti = get_raw_jwt()['jti']

    from flask import current_app
    revoked_token_store.set(
        jti,
        'true',
        current_app.config['JWT_REFRESH_EXPIRES'] * 1.2)
    return jsonify({"message": "Refresh token revoked."}), 200


# A blacklisted access token will not be able to access this any more
@auth.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'hello': 'world'})