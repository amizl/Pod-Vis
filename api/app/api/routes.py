from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from .exceptions import ResourceNotFound, BadRequest
from ..models import db, Study, Project, Subject, SubjectVisit, Observation
import pandas as pd

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
  study = Study.find_by_id(study_id)
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

@api.route("/studies/<study_id>/variables")
def get_study_variables(study_id):
  """Get all variables for a particular study.

  Variables here are the distinct category and scale
  values from the observations tables.
  """

  study = Study.find_by_id(study_id)
  if not study:
    raise ResourceNotFound("Study does not exist.")

  variables = study.get_variables()
  return jsonify({
    "variables": variables
  })

@api.route("/studies/<study_id>/instrument-totals")
def get_totals(study_id):
  """TODO"""
  study = Study.find_by_id(study_id)
  totals = study.total_scores()
  return jsonify(totals)

@api.route("/studies/variables")
def get_intersection_of_variables():
  """Get the intersection of variables between studies."""
  from functools import reduce
  study_ids = request.args.getlist('id')

  studies = [Study.find_by_id(study_id) for study_id in study_ids]
  variables = [study.get_variables() for study in studies]

  # Convert variables result to df to easily perform join. Ideally
  # this might want to be done in SQLAlchemy if performance
  # becomes an issue.
  dfs = [pd.DataFrame(vrbls) for vrbls in variables]
  # Inner join dataframes to find all matching variables
  intersection = reduce((lambda df1, df2: df1.merge(df2)), dfs)

  return jsonify({
    "variables": intersection.to_dict('records')
  })

@api.route('/studies/<study_id>/subjects')
def get_study_subjects(study_id):
  """Get all subjects participating in a study.

  Params:
    include: Other data to include such as :
      1. study
      2. attributes

  Raises:
    ResourceNotFound

  Example URL:
    /api/studies/1/subjects
    /api/studies/1/subjects?include=study&include=attributes
  """
  study = Study.find_by_id(study_id)
  if not study:
    raise ResourceNotFound("Study does not exist.")

  include = request.args.getlist('include')

  kwargs = {
    "include_study": "study" in include,
    "include_attributes": "attributes" in include
  }

  subjects = Subject.find_all_by_study_id(study_id)
  return jsonify({
    "subjects": [subject.to_dict(**kwargs) for subject in subjects]
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
      4. attributes
      To incude project and subjects, user must include study.

  Raises:
    ResourceNotFound
    BadRequest: If query parameters cannot be processed.

  Example request:
    /api/studies/10/subjects/count?group_by=sex
    /api/studies/10/subjects/count?group_by=sex&group_by=race
    /api/studies/10/subjects/count?group_by=race&include=study&include=subjects
  """
  group_by = request.args.getlist("group_by")
  include = request.args.getlist("include")

  study = Study.find_by_id(study_id)
  if not study:
    raise ResourceNotFound(f"The study with ID {study_id} does not exist.")

  try:
    counts = Subject.count(study_id, group_by)
  except KeyError:
    raise BadRequest("There is a problem with the request's query parameters.")

  kwargs = {
    "include_study": "study" in include,
    "include_subjects": "subjects" in include,
    "include_project": "project" in include,
    "include_attributes": "attributes" in include
  }

  response = {
    "counts": counts
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

@api.route('/projects/<project_id>')
def get_project(project_id):
  """Get project data.

  Params:
    include: Data to include from projects. This can currently be:
      1. studies
      2. subjects
      Including subjects can only be used if studies are included.

  Example requests:
    /api/projects/1
    /api/projects/1?include=studies&include=subjects
  """
  project = Project.find_by_id(project_id)
  include = request.args.getlist('include')

  kwargs = {
    "include_studies": "studies" in include,
    "include_subjects": "subjects" in include
  }

  return jsonify({
    "project": project.to_dict(**kwargs)
  })
