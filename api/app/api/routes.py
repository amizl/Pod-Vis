from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_current_user
from functools import reduce
from . import api
from .exceptions import ResourceNotFound, BadRequest
from ..auth.exceptions import AuthFailure
from .. import models
import pandas as pd


@api.route('/subjects')
def get_all_subjects():
    """Get all subjects."""
    subjects = models.Subject.get_all_subjects()
    return jsonify({
        "subjects": [subject.to_dict() for subject in subjects]
    })


@api.route('/studies')
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
    studies = models.Study.get_all_studies()
    include = request.args.getlist("include")

    kwargs = {
        "include_project": "project" in include,
        "include_subjects": "subjects" in include,
    }

    return jsonify({
        "studies": [study.to_dict(**kwargs) for study in studies]
    })


@api.route('/studies/<study_id>')
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
    study = models.Study.find_by_id(study_id)
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

    study = models.Study.find_by_id(study_id)
    if not study:
        raise ResourceNotFound("Study does not exist.")

    variables = study.get_variables()
    return jsonify({
        "variables": variables
    })


@api.route("/studies/<study_id>/instrument-totals")
def get_totals(study_id):
    """TODO"""
    study = models.Study.find_by_id(study_id)
    totals = study.total_scores()
    return jsonify(totals)


@api.route("/studies/variables")
def get_intersection_of_variables():
    """Get the intersection of variables between studies.

    Example URL:
      /api/studies/variables?id=1&id=2
    """
    study_ids = request.args.getlist('id')

    studies = [models.Study.find_by_id(study_id) for study_id in study_ids]
    variables = [study.get_variables() for study in studies]

    # Convert variables result to df to easily perform intersection. Ideally
    # this might want to be done in MySQL/SQLAlchemy if performance
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
    study = models.Study.find_by_id(study_id)
    if not study:
        raise ResourceNotFound("Study does not exist.")

    include = request.args.getlist('include')

    kwargs = {
        "include_study": "study" in include,
        "include_attributes": "attributes" in include
    }

    subjects = models.Subject.find_all_by_study_id(study_id)
    return jsonify({
        "subjects": [subject.to_dict(**kwargs) for subject in subjects]
    })


@api.route('/studies/<study_id>/subjects/attributes')
def get_study_subject_attributes(study_id):
    """Get all attributes for subjects participating in a study.

    Raises:
      ResourceNotFound if study does not exist.

    Example URL:
      /api/studies/1/subjects/attributes
    """
    study = models.Study.find_by_id(study_id)
    if not study:
        raise ResourceNotFound("Study does not exist.")

    subject = models.Subject.find_first_by_study_id(study_id)
    return jsonify({
        "subject_attributes": subject.get_attributes()
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

    study = models.Study.find_by_id(study_id)
    if not study:
        raise ResourceNotFound(f"The study with ID {study_id} does not exist.")

    try:
        counts = models.Subject.count(study_id, group_by)
    except KeyError:
        raise BadRequest(
            "There is a problem with the request's query parameters.")

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
    projects = models.Project.get_all_projects()

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
    project = models.Project.find_by_id(project_id)
    include = request.args.getlist('include')

    kwargs = {
        "include_studies": "studies" in include,
        "include_subjects": "subjects" in include
    }

    return jsonify({
        "project": project.to_dict(**kwargs)
    })

@api.route("/collections", methods=["POST"])
@jwt_required
def create_collection():
    """Create new collection.

    Params:
        label
        studies
        variables
    Example:
        {
            "label": "Test",
            "study_ids": [1,2],
            variables: ["MDS-UPDRS_1"]

        }

    Example requests:
      /api/collections
    """
    request_data = request.get_json()

    user = get_current_user()
    label = request_data.get('label')

    # Create Collection
    collection = models.Collection(user.id, label, 0, 'dynamic')
    collection.save_to_db()

    # Add studies to collection
    study_ids = request_data.get('study_ids')
    collection_studies = []
    for study_id in study_ids:
        study = models.Study.find_by_id(study_id)
        if not study:
            raise ResourceNotFound(
                f"The study with ID {study_id} does not exist.")
        collection_study = models.CollectionStudy(collection.id, study.id)
        collection_study.save_to_db()
        collection_studies.append(collection_study)

    # Add variables to collection
    variables = request_data.get('variables')
    collection_variables = []
    for variable in variables:
        obs_variable = models.CollectionObservationVariable(collection.id, variable)
        obs_variable.save_to_db()
        collection_variables.append(obs_variable)

    return jsonify({
        "collection": collection.to_dict(),
        "collection_studies": [
            collection_study.to_dict()
            for collection_study in collection_studies
        ],
        "collection_variables": [
            collection_variable.to_dict()
            for collection_variable in collection_variables
        ]
    }, 201)

@api.route("/collections")
@jwt_required
def get_collections():
    """Get user's collections.

    Params:
      include: Data to include from collections. This can currently be:
        1. studies
        2. variables

    Example requests:
      /api/collections
      /api/collections?include=studies
      /api/collections?incclude=studies&include=variables
    """
    user = get_current_user()
    collections = models.Collection.find_all_by_user_id(user.id)

    include = request.args.getlist('include')
    kwargs = {
        "include_studies": "studies" in include,
        "include_variables": "variables" in include
    }

    return jsonify({
        "collections": [
            collection.to_dict(**kwargs)
            for collection in collections
        ]
    })

@api.route("/collections/<collection_id>", methods=["DELETE"])
@jwt_required
def delete_collection(collection_id):
    """Delete the user's collection."""
    user = get_current_user()
    collection = models.Collection.find_by_id(collection_id)

    if not collection:
        raise ResourceNotFound("Collection not found.")
    if collection.creator_id != user.id:
        raise AuthFailure('User not authorized to delete collection.')

    collection.delete_from_db()

    return jsonify(dict(success=True))

@api.route("/collections", methods=["DELETE"])
@jwt_required
def delete_all_collections():
    """Delete all of user's collections."""
    user = get_current_user()
    collections = models.Collection.find_all_by_user_id(user.id)

    if not collections:
        raise ResourceNotFound("No collections for user.")

    for collection in collections:
        collection.delete_from_db()

    return jsonify(dict(success=True))
