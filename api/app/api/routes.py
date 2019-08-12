from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_current_user
from scipy.stats import mannwhitneyu
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
        "success": True,
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
        "success": True,
        "studies": [study.to_dict(**kwargs) for study in studies]
    })


@api.route('/studies/<int:study_id>')
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
        "success": True,
        "study": study.to_dict(**kwargs)
    })


@api.route("/studies/<int:study_id>/variables")
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


# @api.route("/studies/<study_id>/instrument-totals")
# def get_totals(study_id):
#     """TODO"""
#     study = models.Study.find_by_id(study_id)
#     totals = study.total_scores()
#     return jsonify(totals)


@api.route("/studies/variables")
def get_intersection_of_variables():
    """Get the intersection of variables between studies.

    Example URL:
      /api/studies/variables?id=1&id=2
    """
    study_ids = request.args.getlist('id')
    studies = [models.Study.find_by_id(study_id) for study_id in study_ids]

    variables = list()

    for study in studies:
        variables.extend(study.get_variables())

    # convert to list of tuples and uniquify with set comprehension
    reduced_vars = [dict(t) for t in {tuple(d.items()) for d in variables}]

    return jsonify({
        "success": True,
        # keys here are 'category', 'scale'
        "variables": reduced_vars
    })


@api.route('/studies/<int:study_id>/subjects')
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
        "success": True,
        "subjects": [subject.to_dict(**kwargs) for subject in subjects]
    })


@api.route('/studies/<int:study_id>/subjects/attributes')
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
        "success": True,
        "subject_attributes": subject.get_attributes()
    })

@api.route('/studies/<int:study_id>/observations')
def get_study_observations(study_id):
    """Get all observations for a study.

    Example URL:
        /api/studies/1/observations
    """
    study = models.Study.find_by_id(study_id)
    if not study:
        raise ResourceNotFound(f"The study with ID {study_id} does not exist.")

    observations = study.get_observations()
    return jsonify({
        "success": True,
        "observations": observations
    })

@api.route('/observations')
def get_all_observations():
    """Get all observations for a study.

    Example URL:
        /api/studies/1/observations
    """
    observations = models.Observation.get_all_observations()

    return jsonify({
        "success": True,
        "observations": observations[0].to_dict()
    })

# @api.route('/studies/<int:study_id>/observations/<int:observation_ontology_id>')
@api.route('/studies/<int:study_id>/variables/<int:observation_ontology_id>/distribution')
def get_study_variable_distribution(study_id, observation_ontology_id):
    """Get observations for a study.

    Aggregates totals for observation.

    Example URL:
        /api/studies/1/observations/43
    """
    study = models.Study.find_by_id(study_id)
    observation = models.ObservationOntology.find_by_id(observation_ontology_id)

    if not study:
        raise ResourceNotFound(f"The study with ID {study_id} does not exist.")
    if not observation:
        raise ResourceNotFound("Observation variable does not exist.")

    observation_counts = study.find_observation_value_counts_by_scale(observation_ontology_id)

    # df_value_counts = pd.DataFrame(observation_counts)
    # # TODO... only do this if type is int but saved as string
    # df_value_counts['value'] = df_value_counts['value'].apply(int)

    return jsonify({
        "success": True,
        "counts": observation_counts,
        # "counts": df_value_counts.sort_values(by="value").to_dict("records"),
        "scale": observation_ontology_id
    })

@api.route('/studies/<int:study_id>/subjects/variables/<int:subject_ontology_id>/distribution')
def get_subject_variable_counts(study_id, subject_ontology_id):
    """Get distribution of a subject variable for a study.

    Example URL:
        /api/studies/1/subject/variables/1/distribution
    """
    study = models.Study.find_by_id(study_id)
    if not study:
        raise ResourceNotFound(f"The study with ID {study_id} does not exist.")
    subject_attribute = models.SubjectOntology.find_by_id(subject_ontology_id)
    if not subject_attribute:
        raise ResourceNotFound(f"The subject attribute with ID {subject_ontology_id} does not exist.")

    subjects = [
        subject.to_dict(include_attributes=True)
        for subject in models.Subject.find_all_by_study_id(study_id)
    ]

    rename_idx = dict()
    rename_idx[subject_attribute.label] = 'value'
    df = pd.DataFrame(subjects) \
        .groupby(subject_attribute.label) \
        .size() \
        .to_frame('count') \
        .reset_index() \
        .rename(columns=rename_idx)

    return jsonify({
        "success": True,
        "counts": df.to_dict("records"),
        "scale": subject_attribute.label,
        "subject_ontology_id": subject_attribute.label
    })

@api.route('/studies/<int:study_id>/subjects/count')
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
        "success": True,
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
        "success": True,
        "projects": [
            project.to_dict(**kwargs)
            for project in projects
        ]
    })


@api.route('/projects/<int:project_id>')
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
        "success": True,
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
    label = request_data.get('label')
    study_ids = request_data.get('study_ids')
    variables = request_data.get('variables')

    if not study_ids:
        raise BadRequest("A collection must have studies.")
    if not variables:
        raise BadRequest("A collection must have variables.")

    user = get_current_user()

    # Create Collection
    collection = models.Collection(user.id, label, 0, 'dynamic')
    collection.save_to_db()

    # Add studies to collection
    for study_id in study_ids:
        study = models.Study.find_by_id(study_id)
        if not study:
            raise ResourceNotFound(
                f"The study with ID {study_id} does not exist.")
        collection_study = models.CollectionStudy(collection.id, study.id)
        collection_study.save_to_db()

    # Add variables to appropriate collection table
    for variable in variables:
        if variable["type"] == "observation":
            obs_variable = models.CollectionObservationVariable(collection.id, variable["id"])
            obs_variable.save_to_db()
        elif variable["type"] == "subject":
            subject_variable = models.CollectionSubjectVariable(collection.id, variable["id"])
            subject_variable.save_to_db()
        else:
            # This should never happen but just in case it does...
            raise BadRequest("Variable has unsupported type.")

    return jsonify({
        "success": True,
        "collection": collection.to_dict(include_studies=True, include_variables=True)
    }), 201

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
        "success": True,
        "collections": [
            collection.to_dict(**kwargs)
            for collection in collections
        ]
    })

@api.route("/collections/<int:collection_id>")
@jwt_required
def get_collection(collection_id):
    """Get the user's collection."""
    user = get_current_user()
    collection = models.Collection.find_by_id(collection_id)

    if not collection:
        raise ResourceNotFound("Collection not found.")
    if collection.user_id != user.id:
        raise AuthFailure('User not authorized to retrieve collection.')

    include = request.args.getlist('include')
    kwargs = {
        "include_studies": "studies" in include,
        "include_variables": "variables" in include
    }

    return jsonify(dict(success=True, collection=collection.to_dict(**kwargs)))

@api.route("/collections/<int:collection_id>", methods=["DELETE"])
@jwt_required
def delete_collection(collection_id):
    """Delete the user's collection."""
    user = get_current_user()
    collection = models.Collection.find_by_id(collection_id)

    if not collection:
        raise ResourceNotFound("Collection not found.")
    if collection.user_id != user.id:
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
        raise ResourceNotFound("No collections to delete for user.")

    for collection in collections:
        collection.delete_from_db()

    return jsonify(dict(success=True))

@api.route("/cohorts")
@jwt_required
def get_all_cohorts():
    """Get all of user's cohorts.

    Example URL:
    /api/cohorts
    /api/cohorts?include=subjects
    """
    user = get_current_user()
    cohorts = models.Cohort.find_all_by_user_id(user.id)

    include = request.args.getlist('include')
    kwargs = {
        "include_subjects": "subjects" in include,
    }

    return jsonify({
        "success": True,
        "cohorts": [
            cohort.to_dict(**kwargs)
            for cohort in cohorts
        ]
    })

@api.route("/cohorts/<int:cohort_id>")
@jwt_required
def get_cohort(cohort_id):
    """Get a user's cohort.

    Params:
        subjects

    Example URL:
    /api/cohorts/1
    /api/cohorts/1?include=subjects
    """
    user = get_current_user()
    cohort = models.Cohort.find_by_id(cohort_id)

    if user.id != cohort.user_id:
        raise AuthFailure("User does not own this cohort.")

    include = request.args.getlist('include')
    kwargs = {
        "include_subjects": "subjects" in include,
    }

    return jsonify({
        "success": True,
        "cohort": cohort.to_dict(**kwargs)
    })


# @api.route('/cohorts', methods=["POST"])
# @jwt_required
# def create_cohort():
#     """Create new cohort.

#     Example requests:
#       /api/cohorts
#     """
#     request_data = request.get_json()

#     user = get_current_user()
#     label = request_data.get('label')

#     # Create Collection
#     cohort = models.Cohort(user.id, label, 'dynamic')
#     cohort.save_to_db()

#     # Add subjects to cohort
#     # TODO

#     # Add queries to cohort
#     # TODO
#     return jsonify({
#         "success": True,
#         "cohort": cohort.to_dict()
#     }), 201

@api.route('/cohorts', methods=["DELETE"])
@jwt_required
def delete_all_cohorts():
    """Delete all of user's cohorts.

    Example requests:
      /api/cohorts
    """
    user = get_current_user()
    cohorts = models.Cohort.find_all_by_user_id(user.id)

    if not cohorts:
        raise ResourceNotFound("This user has no cohorts to delete.")

    for cohort in cohorts:
        cohort.delete_from_db()

    return jsonify({
        "success": True,
    })

@api.route('/cohorts/<int:cohort_id>', methods=["DELETE"])
@jwt_required
def delete_cohort(cohort_id):
    """Delete user's cohort.

    Example requests:
      /api/cohorts
    """
    user = get_current_user()
    cohort = models.Cohort.find_by_id(cohort_id)

    if not cohort:
        raise ResourceNotFound("Cohort does not exist.")

    if user.id != cohort.user_id:
        raise AuthFailure("Not authorized to delete this cohort.")

    cohort.delete_from_db()

    return jsonify({
        "success": True,
    })

@api.route('/collections/<int:collection_id>/observations/<int:observation_id>/roc')
@jwt_required
def compute_roc_for_observation(collection_id, observation_id):
    user = get_current_user()
    collection = models.Collection.find_by_id(collection_id)
    observation = models.ObservationOntology.find_by_id(observation_id)

    if not collection:
        raise ResourceNotFound("Collection does not exist.")
    if not observation:
        raise ResourceNotFound("Observation variable does not exist.")
    if user.id != collection.user_id:
        raise AuthFailure('Not authorized to use this collection.')
    if not collection.contains_observation(observation_id):
        raise ResourceNotFound("Collection does not contain this observation.")

    ROC = collection.compute_roc_across_visits_for_scale(observation_id)

    return jsonify({
        "success": True
    })


@api.route('/cohort-manager')
@jwt_required
def fetch_data_for_cohort_manager():
    """Fetch data from studies and variables included in a collection"""
    user = get_current_user()
    request_data = request.get_json()
    collection_id = request.args.get("collection")
    collection = models.Collection.find_by_id(collection_id)

    if not collection:
        raise ResourceNotFound("Collection does not exist.")
    if user.id != collection.user_id:
        raise AuthFailure("Not authorized to use this collection.")

    data = collection.get_data_for_cohort_manager()

    return jsonify({
        "success": True,
        "data": data.to_json(orient="records", date_format='iso')
    })


@api.route('/demo-parcoords')
@jwt_required
def demo_parcoords():
    """Fetch data from studies and variables included in a collection"""
    user = get_current_user()
    request_data = request.get_json()
    collection_id = request.args.get("collection")
    collection = models.Collection.find_by_id(collection_id)

    if not collection:
        raise ResourceNotFound("Collection does not exist.")
    if user.id != collection.user_id:
        raise AuthFailure("Not authorized to use this collection.")

    data = collection.proof_of_concept_parcoords()

    return jsonify({
        "success": True,
        "data": data
#        "data": data.to_json(orient="records", date_format='iso')
    })

@api.route('/compute-mannwhitneyu', methods=['POST'])
def compute_mannwhitneyu():
    """Compute Mann-Whitney rank test"""
    request_data = request.get_json()
    filtered_data = request_data.get("filteredData")
    unfiltered_data = request_data.get("unfilteredData")
    output_variables = request_data.get("outputVariables")

    pvals = []
    for output_variable in output_variables:
        # Output variables that are simply "change" or "firstVisit" will have the
        # id of "change-208" or "firstVisit-208". We want to detect this so we can
        # use the correct id
        if isinstance(output_variable.get("id"), str) and "-" in output_variable.get("id"):
            variable_id = str(output_variable.get("parentID"))
            variable_label = output_variable.get("parentLabel")
        else:
            variable_id = str(output_variable.get("id"))
            variable_label = output_variable.get("label")

        filtered_first_visit_sample = [data.get(variable_id).get('change') for data in filtered_data]
        unfiltered_last_visit_sample = [data.get(variable_id).get('change') for data in unfiltered_data]
        stats, pval = mannwhitneyu(filtered_first_visit_sample, unfiltered_last_visit_sample)
        pvals.append(dict(label=variable_label, pval=pval))

    return jsonify({
        "success": True,
        "pvals": pvals,
    })

@api.route('/cohorts', methods=['POST'])
@jwt_required
def create_cohort():
    """Create cohort"""
    request_data = request.get_json()
    queries = request_data.get("queries")
    cohort_subjects = request_data.get("cohort_subjects")
    cohort_name = request_data.get("cohort_name")
    collection_id = request_data.get("collection_id")
    instantiation_type = 'dynamic'

    if not queries or not cohort_subjects or not cohort_name or not collection_id:
        raise BadRequest("Missing payload data to complete request.")

    user = get_current_user()

    collection = models.Collection.find_by_id(collection_id)
    if not collection:
        raise ResourceNotFound("Collection does not exist.")
    if user.id != collection.user_id:
        raise AuthFailure("Not authorized to use this collection.")

    # create cohort
    cohort = models.Cohort(user.id, cohort_name, collection.id, instantiation_type)
    cohort.save_to_db()

    # for query in queries:

    #     query = models.CohortQuery(cohort.id, )

    return jsonify({
        "success": True,
        "cohort": cohort.to_dict()
    }), 201
    # creat query
    # create subjects



    # Add studies to collection
