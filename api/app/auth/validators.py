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
        validation = SignInSchema().load(request_data)
        if validation.errors:
            raise AuthFailure(validation.errors)
        else:
            return func(*args, **kwargs)
    return wrapper

def validate_sign_up(func):
    """"Valdate sign up form data."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_data = request.get_json()
        validation = SignUpSchema().load(request_data)
        if validation.errors:
            raise AuthFailure(validation.errors)
        else:
            return func(*args, **kwargs)
    return wrapper
