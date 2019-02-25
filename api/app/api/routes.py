from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
# from .exceptions import ApiFailure
from ..models import db, Study, Project, DatasetAdded

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


@api.route('/datasets-added')
@jwt_required
def get_all_datasets_user_added_to_profile():
  user_id = get_jwt_identity()
  datasets = DatasetAdded.find_all_by_user_id(user_id)
  return jsonify({
    "datasets": list(map(lambda dataset: dataset.to_dict()), datasets)
  })

@api.route('/datasets-added', methods=['POST'])
@jwt_required
def add_dataset_to_profile():
  user_id = get_jwt_identity()

  request_data = request.get_json()
  study_id = request_data.get('study_id')

  # will want to try catch if duplicate entry...
  new_dataset = DatasetAdded(user_id, study_id)
  new_dataset.save_to_db()

  return jsonify({
    "dataset": new_dataset.to_dict()
  })