from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from .exceptions import ResourceNotFound, BadRequest
from ..models import db, Study, Project, Subject

@api.route('/subjects')
# @jwt_required
def get_all_subjects():
  """Get all subjects."""
  subjects = Subject.get_all_subjects()
  return jsonify({
    "subjects": [subject.to_dict() for subject in  subjects]
  })

@api.route('/studies')
# @jwt_required
def get_all_studies():
  """Get all studies."""
  studies = Study.get_all_studies()
  return jsonify({
    "studies": [study.to_dict() for study in studies]
  })

@api.route('/studies/<study_id>')
# @jwt_required
def get_study(study_id):
  """Get study by its ID."""
  study = Study.find_by_study_id(study_id)
  if study:
    return jsonify({
      "study": study.to_dict()
    })
  else:
    raise ResourceNotFound("Study does not exist.")

@api.route('/studies/<study_id>/subjects')
def get_study_subjects(study_id):
  """Get all subjects participating in a study."""
  study = Study.find_by_study_id(study_id)
  if not study:
    raise ResourceNotFound("Study does not exist.")

  subjects = Subject.find_all_by_study_id(study_id)
  return jsonify({
    "subjects": [subject.to_dict() for subject in subjects]
  })

@api.route('/studies/<study_id>/subjects/count')
def summarize_study_subjects(study_id):
  """Get summarized counts from subjects.

  Params:
    group_by: Attributes to group on.

  Raises:
    BadRequest: If query parameters cannot be processed.

  Example request:
    /api/studies/10/subjects/count?group_by=sex&group_by=race
  """
  group_by = request.args.getlist("group_by")

  study = Study.find_by_study_id(study_id)
  if not study:
    raise ResourceNotFound(f"The study with ID {study_id} does not exist.")

  try:
    counts = Subject.count(study_id, group_by)
  except AttributeError:
    raise BadRequest("There is a problem with the request's query parameters.")

  return jsonify({
    "counts": [count._asdict() for count in counts]
  })

@api.route('/projects')
def get_all_projects():
  """Get all projects.

  Params:
    include: Data to include from projects. This can currently be:
      1. studies
      2. subjects
      Including subjects can only be used if studies are included.

  Example requests:
    /api/projects
    /api/projects?include=studies&include=subjects
  """
  projects = Project.get_all_projects()

  includes = request.args.getlist('include')
  kwargs = {
    "include_studies": "studies" in includes,
    "include_subjects": "subjects" in includes
  }

  return jsonify({
    "projects": [
      project.to_dict(**kwargs)
      for project in projects
    ]
  })
