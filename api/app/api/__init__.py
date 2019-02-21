from flask import Blueprint, jsonify, Request
from flask_jwt_extended import jwt_required
api = Blueprint("api", __name__)

@api.route('/')
@jwt_required
def hello():
  return "Hello World..."
