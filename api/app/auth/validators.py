from functools import wraps
from flask import request, jsonify
from marshmallow import Schema, fields
from .exceptions import AuthFailure

class SignInSchema(Schema):
    """Schema for validating sign in request."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class SignUpSchema(Schema):
    """Schema for validating sign up request."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    institution = fields.Str(required=True)
    name = fields.Str(required=True)

def validate_sign_in(func):
    """Validate sign in form data."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_data = request.get_json()
        data, errors = SignInSchema().load(request_data)
        if errors:
            raise AuthFailure(errors)
        else:
            email = data.get("email")
            password = data.get("password")
            return func(email, password)
    return wrapper

def validate_sign_up(func):
    """"Valdate sign up form data."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_data = request.get_json()
        data, errors = SignUpSchema().load(request_data)
        if errors:
            raise AuthFailure(errors)
        else:
            email = data.get("email")
            password = data.get("password")
            institution = data.get("institution")
            name = data.get("name")
            return func(email, password, institution, name)
    return wrapper
