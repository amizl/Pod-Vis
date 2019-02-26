from functools import wraps
from flask import request, jsonify
# Because are we submitting these forms as application/json,
# there is no form data. We utilize the MultiDict function
# in order to wrap our request data in to a data structure that
# Flask Forms will accept.
from werkzeug.datastructures import MultiDict
from .exceptions import AuthFailure
from ..forms import SignInForm, SignUpForm

def validate_sign_in(func):
    """Validate sign in form data."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_data = MultiDict(mapping=request.get_json())
        sign_in_form = SignInForm(request_data)
        if sign_in_form.validate():
            return func(*args, **kwargs)
        else:
            raise AuthFailure(sign_in_form.errors)
    return wrapper

def validate_sign_up(func):
    """"Valdate sign up form data."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_data = MultiDict(mapping=request.get_json())
        sign_up_form = SignUpForm(request_data)
        if sign_up_form.validate():
            return func(*args, **kwargs)
        else:
            raise AuthFailure(sign_up_form.errors)
    return wrapper
