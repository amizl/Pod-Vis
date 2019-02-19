from flask import Blueprint, jsonify, Request

api = Blueprint("api", __name__)

@api.route('/')
def hello():
  return "Hello World..."
