from flask import jsonify
from . import api

class ApiFailure(Exception):
    """Base class Exception for API failure."""
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def to_dict(self):
        rv = dict()
        rv['error'] = self.message
        return rv


class ResourceNotFound(ApiFailure):
    """Exception for endpoint failing to find resource."""
    status_code = 404
    def __init__(self, message):
        super().__init__(message)


class BadRequest(ApiFailure):
    """Exception for endpoint failing because of a bad request."""
    status_code = 400
    def __init__(self, message):
        super().__init__(message)


@api.errorhandler(ApiFailure)
def handle_auth_failure(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response