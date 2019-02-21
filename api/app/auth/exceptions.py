from flask import jsonify
from . import auth

class AuthFailure(Exception):
    """Exception for failing to authenticate user."""
    status_code = 401

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def to_dict(self):
        rv = dict()
        rv['error'] = self.message
        return rv

@auth.errorhandler(AuthFailure)
def handle_auth_failure(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

