from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
# from .exceptions import ApiFailure
from ..models import db, Study, Project

@api.route('/studies')
@jwt_required
def get_all_studies():
  """Return all studies."""
  studies = Study.get_all_studies()
  return jsonify({
    "studies": list(map(lambda study: study.to_dict(), studies))
  })

@api.route('/projects')
def get_all_projects():
  projects = Project.get_all_projects()
  return jsonify({
    "projects": list(map(lambda project: project.to_dict(), projects))
  })