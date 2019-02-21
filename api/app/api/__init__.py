from flask import Blueprint, jsonify, Request
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint("api", __name__)

@api.route('/')
@jwt_required
def foo():
  identity = get_jwt_identity()
  return jsonify({"user_id": identity})
