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
  """Get all studies.

  Params:
    include: Query to include other data such as:
      1. project
      2. subjects

  Example URL:
    /api/studies
    /api/studies?include=project&include=subjects
  """
  studies = Study.get_all_studies()
  include = request.args.getlist("include")

  kwargs = {
    "include_project": "project" in include,
    "include_subjects": "subjects" in include,
  }

  return jsonify({
    "studies": [study.to_dict(**kwargs) for study in studies]
  })

@api.route('/studies/<study_id>')
# @jwt_required
def get_study(study_id):
  """Get study by its ID.

  Params:
    include: Query to include other data such as:
      1. project
      2. subjects

  Example URL:
    /api/studies/10
    /api/studies/10?include=project&include=subjects
  """
  study = Study.find_by_study_id(study_id)
  include = request.args.getlist("include")

  if not study:
    raise ResourceNotFound("Study does not exist.")

  kwargs = {
    "include_project": "project" in include,
    "include_subjects": "subjects" in include
  }

  return jsonify({
    "study": study.to_dict(**kwargs)
  })

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
    include: Other data to include such as:
      1. study
      2. project
      3. subjects
      To incude project and subjects, user must include study.

  Raises:
    BadRequest: If query parameters cannot be processed.

  Example request:
    /api/studies/10/subjects/count?group_by=sex
    /api/studies/10/subjects/count?group_by=sex&group_by=race
    /api/studies/10/subjects/count?group_by=race&include=study&include=subjects
  """
  group_by = request.args.getlist("group_by")
  include = request.args.getlist("include")

  study = Study.find_by_study_id(study_id)
  if not study:
    raise ResourceNotFound(f"The study with ID {study_id} does not exist.")

  try:
    counts = Subject.count(study_id, group_by)
  except AttributeError:
    raise BadRequest("There is a problem with the request's query parameters.")


  kwargs = {
    "include_study": "study" in include,
    "include_subjects": "subjects" in include,
    "include_project": "project" in include,
  }

  response = {
    "counts": [count._asdict() for count in counts]
  }

  if "study" in include:
    response['study'] = study.to_dict(**kwargs)

  return jsonify(response)

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

  include = request.args.getlist('include')
  kwargs = {
    "include_studies": "studies" in include,
    "include_subjects": "subjects" in include
  }

  return jsonify({
    "projects": [
      project.to_dict(**kwargs)
      for project in projects
    ]
  })
