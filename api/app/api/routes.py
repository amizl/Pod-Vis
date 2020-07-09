from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_current_user
from scipy.stats import mannwhitneyu, f_oneway
from functools import reduce
from . import api
from .exceptions import ResourceNotFound, BadRequest
from ..auth.exceptions import AuthFailure
from .. import models
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import sys

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

@api.route("/studies/attributes")
def get_intersection_of_attributes():
    """Get the intersection of subject attributes between studies.

    Example URL:
      /api/studies/attributes?id=1&id=2
    """
    study_ids = request.args.getlist('id')
    subj_atts = models.Study.get_subject_attributes(study_ids)

    return jsonify({
        "success": True,
        "attributes": subj_atts
    })

@api.route("/studies/subject_variables")
def get_subject_variables():
    """Retrieve all subjects for a set of studies, along with the variables supported by those subjects.

    Example URL:
      /api/studies/subject_variables?id=1&id=2
    """
    study_ids = request.args.getlist('id')

    subjects = models.Study.get_subject_variables(study_ids)

#    studies = [models.Study.find_by_id(study_id) for study_id in study_ids]
#    variables = list()
#    for study in studies:
#        variables.extend(study.get_variables())
    # convert to list of tuples and uniquify with set comprehension
#    reduced_vars = [dict(t) for t in {tuple(d.items()) for d in variables}]

    return jsonify({
        "success": True,
        "subjects": subjects
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

    subj_atts = models.Study.get_subject_attributes([study_id])
    return jsonify({
        "success": True,
        "subject_attributes": subj_atts
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

    observation_counts = study.find_observation_value_counts_by_scale(observation)

    # df_value_counts = pd.DataFrame(observation_counts)
    # # TODO... only do this if type is int but saved as string
    # df_value_counts['value'] = df_value_counts['value'].apply(int)

    return jsonify({
        "success": True,
        "counts": observation_counts,
        # "counts": df_value_counts.sort_values(by="value").to_dict("records"),
        "scale": observation_ontology_id,
        "value_type": observation.value_type.name,
        "data_category": observation.data_category.name,
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

    counts = models.Subject.get_study_subjects_variable_counts(study_id, subject_ontology_id)
        
    return jsonify({
        "success": True,
        "counts": counts,
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
        "include_subjects": "subjects" in include,
        "include_num_subjects": "num_subjects" in include,
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

    # Add special "Dataset" subject variable
    dataset_var = models.SubjectOntology.find_by_label("Dataset")
    # ...creating it if it does not exist
    if dataset_var is None:
        dataset_var = models.SubjectOntology(None, 'Dataset', 'char', 'Categorical');
        dataset_var.save_to_db()
        
    subj_var = models.CollectionSubjectVariable(collection.id, dataset_var.id)
    subj_var.save_to_db()
        
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

@api.route("/collections/<int:collection_id>/observation_visits", methods=["POST"])
@jwt_required
def set_collection_observation_variable_visits(collection_id):
    """Set first/last visit for observation variable(s).

    Params:
        variable_visits
    Example:
        {
            "variable_visits": [ {"variable_id": "2", "first_visit_event": "BL", "last_visit_event": "V12"} ],
        }

    Example requests:
      /api/collections/23/observation_visits
    """
    request_data = request.get_json()
    variable_visits = request_data.get('variable_visits')

    if not variable_visits:
        raise BadRequest("No observation variable first/last visits specified.")

    user = get_current_user()
    collection = models.Collection.find_by_id(collection_id)
    
    if not collection:
        raise ResourceNotFound("Collection not found.")
    if (collection.is_public) == 0 and (collection.user_id != user.id):
        raise AuthFailure('User not authorized to retrieve collection.')

    obs_vars = collection.observation_variables
    vvh = {}
    for vv in variable_visits:
        vvh[vv['variable_id']] = vv

    for ov in obs_vars:
        vv = vvh[ov.observation_ontology_id]
        if 'first_visit_event' in vv:
            ov.first_visit_event = vv['first_visit_event']
        if 'last_visit_event' in vv:
            ov.last_visit_event = vv['last_visit_event']
        if 'first_visit_num' in vv:
            ov.first_visit_num = vv['first_visit_num']
        if 'last_visit_num' in vv:
            ov.last_visit_num = vv['last_visit_num']
        ov.save_to_db()
        
    return jsonify({
        "success": True,
    }), 201

@api.route("/collections")
@jwt_required
def get_collections():
    """Get user's collections and any public collections.

    Params:
      include: Data to include from collections. This can currently be:
        1. studies
        2. variables
        3. cohort_counts

    Example requests:
      /api/collections
      /api/collections?include=studies
      /api/collections?include=studies&include=variables
    """
    user = get_current_user()
    collections = models.Collection.find_all_by_user_id(user.id)
    pub_collections = models.Collection.find_all_public()

    # add only public collections not owned by user
    for c in pub_collections:
        if (c.user_id != user.id):
            collections.append(c)
    
    include = request.args.getlist('include')
    kwargs = {
        "include_studies": "studies" in include,
        "include_variables": "variables" in include,
        "include_cohort_counts": "cohort_counts" in include,
        # only count cohorts owned by the current user
        "cohort_user_id": user.id
    }

    # convert to list of dicts
    collection_dicts = []
    for c in collections:
        d = c.to_dict(**kwargs)
        d['is_deletable'] = (c.user_id == user.id)
        collection_dicts.append(d)
    
    return jsonify({
        "success": True,
        "collections": collection_dicts
    })

@api.route("/collections/<int:collection_id>")
@jwt_required
def get_collection(collection_id):
    """Get the user's collection."""
    user = get_current_user()
    collection = models.Collection.find_by_id(collection_id)

    if not collection:
        raise ResourceNotFound("Collection not found.")
    if (collection.is_public) == 0 and (collection.user_id != user.id):
        raise AuthFailure('User not authorized to retrieve collection.')

    include = request.args.getlist('include')
    kwargs = {
        "include_studies": "studies" in include,
        "include_variables": "variables" in include
    }

    collection_d = collection.to_dict(**kwargs)

    # add scale categories
    get_obs_scale_category = models.ObservationOntology.get_var_category_fn()
    for ov in collection_d['observation_variables']:
        if 'ontology' in ov:
            oo = ov['ontology']
            oo['category'] = get_obs_scale_category(oo['id'])

    get_subj_scale_category = models.SubjectOntology.get_var_category_fn()
    for sv in collection_d['subject_variables']:
        if 'ontology' in sv:
            so = sv['ontology']
            so['category'] = get_subj_scale_category(so['id'])

    return jsonify(dict(success=True, collection=collection_d))

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

    cohorts_l = [
        cohort.to_dict(**kwargs)
        for cohort in cohorts
    ]
    
    # add scale categories
    get_obs_scale_category = models.ObservationOntology.get_var_category_fn()
    get_subj_scale_category = models.SubjectOntology.get_var_category_fn()

    for c in cohorts_l:
        for ov in c['output_variables']:
            if 'observation_ontology' in ov:
                oo = ov['observation_ontology']
                oo['category'] = get_obs_scale_category(oo['id'])
        for iv in c['input_variables']:
            if 'subject_ontology' in iv:
                so = iv['subject_ontology']
                so['category'] = get_subj_scale_category(so['id'])
            if 'observation_ontology' in iv:
                oo = iv['observation_ontology']
                oo['category'] = get_obs_scale_category(oo['id'])
                
    return jsonify({
        "success": True,
        "cohorts": cohorts_l
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
    if (collection.is_public) == 0 and (collection.user_id != user.id):
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
    if (collection.is_public) == 0 and (collection.user_id != user.id):
        raise AuthFailure("Not authorized to use this collection.")

    data = collection.get_data_for_cohort_manager()

    return jsonify({
        "success": True,
        "data": "{ \"data\": " + data['data'].to_json(orient="records", date_format='iso') + "\n, \"raw_data\": " + data['raw_data'].to_json(orient="records", date_format='iso') + "}"
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
    if (collection.is_public) == 0 and (collection.user_id != user.id):
        raise AuthFailure("Not authorized to use this collection.")

    data = collection.proof_of_concept_parcoords()

    return jsonify({
        "success": True,
        "data": data
#        "data": data.to_json(orient="records", date_format='iso')
    })

@api.route('/compute-anova', methods=['POST'])
def compute_anova():
    """Compute 1-way ANOVA test"""
    request_data = request.get_json()
    groups = request_data.get("groups")
    output_variables = request_data.get("outputVariables")

    pvals = []

    for output_variable in output_variables:
        # test doesn't apply to longitudinal categorical variables
        if output_variable['data_category'] == 'Categorical':
            continue

        # Output variables that are simply "change" or "firstVisit" will have the
        # id of "change-208" or "firstVisit-208". We want to detect this so we can
        # use the correct id
        if isinstance(output_variable.get("id"), str) and "-" in output_variable.get("id"):
            variable_id = str(output_variable.get("parentID"))
            variable_label = output_variable.get("parentLabel")
        else:
            variable_id = str(output_variable.get("id"))
            variable_label = output_variable.get("label")

        samples = []
        for g in groups:
            sample = []
            for data in g:
                change = data.get(variable_id).get('change')
                if change is not None:
                    sample.append(float(change))
            samples.append(sample)
            
        fval, pval = f_oneway(*samples)
        pvals.append(dict(label=variable_label, pval=pval, fval=fval))
         
    return jsonify({
        "success": True,
        "pvals": pvals,
    })

@api.route('/compute-pairwise-tukeyhsd', methods=['POST'])
def compute_pairwise_tukeyhsd():
    """Compute Tukey HSD test"""
    request_data = request.get_json()
    groups = request_data.get("groups")
    output_variables = request_data.get("outputVariables")
    results = {}

    for output_variable in output_variables:
        # test doesn't apply to longitudinal categorical variables
        if output_variable['data_category'] == 'Categorical':
            continue

        if isinstance(output_variable.get("id"), str) and "-" in output_variable.get("id"):
            variable_id = str(output_variable.get("parentID"))
            variable_label = output_variable.get("parentLabel")
        else:
            variable_id = str(output_variable.get("id"))
            variable_label = output_variable.get("label")

        groupnums = []
        data = []
        
        for g in groups:
            for datum in g['data']:
                groupnums.append(g['id'])
                change = datum.get(variable_id).get('change')
                if change is not None:
                    data.append(change)

        # compute Tukey-HSD
        res = pairwise_tukeyhsd(groups=groupnums, endog=data)
        results[variable_label] = {
            'label': variable_label,
            'unique_groups': [x.item() for x in list(res.groupsunique)],
            'pvals': [x.item() for x in list(res.pvalues)],
            'reject': [True if x else False for x in list(res.reject) ]}

    return jsonify({
        "success": True,
        "results": results,
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
        # test doesn't apply to longitudinal categorical variables
        if output_variable['data_category'] == 'Categorical':
            continue
        
        # Output variables that are simply "change" or "firstVisit" will have the
        # id of "change-208" or "firstVisit-208". We want to detect this so we can
        # use the correct id
        if isinstance(output_variable.get("id"), str) and "-" in output_variable.get("id"):
            variable_id = str(output_variable.get("parentID"))
            variable_label = output_variable.get("parentLabel")
        else:
            variable_id = str(output_variable.get("id"))
            variable_label = output_variable.get("label")

        # ignore parent ontology terms with no actual data
        # TODO - filter these correctly on the client side
        if unfiltered_data is not None:
            if unfiltered_data[0].get(variable_id) is None:
                continue

        filtered_sample = [data.get(variable_id).get('change') for data in filtered_data]
        unfiltered_sample = [data.get(variable_id).get('change') for data in unfiltered_data]

        err = None
        n_filtered = len(filtered_sample)
        n_unfiltered = len(unfiltered_sample)
        if n_filtered < 20:
            err = "Filtered sample size < 20"
        elif n_unfiltered < 20:
            err = "Unfiltered sample size < 20"
            
        # TODO - use of 'None' default for alternative is deprecated, see https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
        u, pval = mannwhitneyu(filtered_sample, unfiltered_sample, alternative='two-sided')

        # common language effect size f = U/(n1 * n2)
        f = u / (n_filtered * n_unfiltered)
        
        pvals.append(dict(label=variable_label,
                          test_name='2-Sided Mann-Whitney U Test',
                          test_abbrev='2SMWU',
                          pval=pval,
                          effect_size=f,
                          effect_size_descr='Common language effect size.',
                          u_statistic=u,
                          error=err))

    return jsonify({
        "success": True,
        "pvals": pvals,
    })

@api.route('/cohorts', methods=['POST'])
@jwt_required
def create_cohort():
    """Create cohort"""

    # TODO: Break this function up to follow SOLID principles

    request_data = request.get_json()
    queries = request_data.get("queries")
    input_variables = request_data.get("input_variables", [])
    output_variables = request_data.get("output_variables", [])
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
    if (collection.is_public) == 0 and (collection.user_id != user.id):
        raise AuthFailure("Not authorized to use this collection.")

    # create cohort
    cohort = models.Cohort(user.id, cohort_name, collection.id, instantiation_type)
    cohort.save_to_db()

    # Label checks need to be refactored into their own method
    for output_variable in output_variables:
        # If an output variable has children, then the entire outcome
        # variable was selected and need to be unrolled
        if "children" in output_variable:
            for child_output_variable in output_variable['children']:
                # Needs to be refactored. The labels being hard coded to 'First Visit", etc,
                # mismatches our schema's enums.
                if child_output_variable['label'] == 'First Visit':
                    dimension_label = 'left_y_axis'
                elif child_output_variable['label'] == 'Last Visit':
                    dimension_label = 'right_y_axis'
                elif child_output_variable['label'] == 'Rate of Change':
                    dimension_label = 'roc'
                elif child_output_variable['label'] == 'Change':
                    dimension_label = 'change'
                new_output_variable = models.CohortOutputVariable(
                    cohort.id,
                    observation_ontology_id = child_output_variable['parentID'],
                    dimension_label = dimension_label)
                new_output_variable.save_to_db()
        # variable from cross-sectional study
        elif not output_variable['is_longitudinal']:
            new_output_variable = models.CohortOutputVariable(
                cohort.id,
                observation_ontology_id = output_variable['id'],
                dimension_label = None)
            new_output_variable.save_to_db()
        else:
            if output_variable['label'] == 'First Visit':
                dimension_label = 'left_y_axis'
            elif output_variable['label'] == 'Last Visit':
                dimension_label = 'right_y_axis'
            elif output_variable['label'] == 'Rate of Change':
                dimension_label = 'roc'
            elif output_variable['label'] == 'Change':
                dimension_label = 'change'
            new_output_variable = models.CohortOutputVariable(
                cohort.id,
                observation_ontology_id = output_variable['parentID'],
                dimension_label = dimension_label)
            new_output_variable.save_to_db()

    # save all input variables in the database
    input_vars = {}
    for variable in input_variables:
        variable_type = variable['type']

        if variable_type == 'subject' or variable_type == 'study':
            input_variable = models.CohortInputVariable(cohort.id, subject_ontology_id = variable['id'])
        else:
            # type is observation

            # variable from cross-sectional study
            if not variable['is_longitudinal']:
                input_variable = models.CohortInputVariable(
                    cohort.id,
                    observation_ontology_id = variable['id'],
                    dimension_label = None)

            else:
                # Needs to be refactored. The labels being hard coded to 'First Visit", etc,
                # mismatches our schema's enums.
                if variable['label'] == 'First Visit':
                    dimension_label = 'left_y_axis'
                elif variable['label'] == 'Last Visit':
                    dimension_label = 'right_y_axis'
                elif variable['label'] == 'Rate of Change':
                    dimension_label = 'roc'
                elif variable['label'] == 'Change':
                    dimension_label = 'change'

                input_variable = models.CohortInputVariable(
                    cohort.id,
                    observation_ontology_id = variable['parentID'],
                    dimension_label = dimension_label)
                
        input_variable.save_to_db()
        input_vars[variable['id']] = input_variable
        
    for query in queries:
        variable = query['variable']
        input_variable = input_vars[variable['id']]
        
        variable_queries = query['query']
        for variable_query in variable_queries:
            if "value" in variable_query:
                query = models.CohortQuery(
                    cohort.id,
                    input_variable.id,
                    value = variable_query["value"])
                query.save_to_db()
            elif "minValue" in variable_query and "maxValue" in variable_query:
                query = models.CohortQuery(
                    cohort.id,
                    input_variable.id,
                    min_value = variable_query["minValue"],
                    max_value = variable_query["maxValue"])
                query.save_to_db()

    # TODO: Save cohort subjects to cohort_subject table
    cohort_d = cohort.to_dict()

    # add scale categories
    get_obs_scale_category = models.ObservationOntology.get_var_category_fn()
    for ov in cohort_d['output_variables']:
        if 'observation_ontology' in ov:
            oo = ov['observation_ontology']
            oo['category'] = get_obs_scale_category(oo['id'])

    get_subj_scale_category = models.SubjectOntology.get_var_category_fn()
    for iv in cohort_d['input_variables']:
        if 'subject_ontology' in iv:
            so = iv['subject_ontology']
            so['category'] = get_subj_scale_category(so['id'])
        if 'observation_ontology' in iv:
            oo = iv['observation_ontology']
            oo['category'] = get_obs_scale_category(oo['id'])

    return jsonify({
        "success": True,
        "cohort": cohort_d
    }), 201

# Method to retrieve all collection observation summaries
@api.route("/collections/obs_summaries/<int:collection_id>")
@jwt_required
def get_collection_obs_summary_by_event(collection_id):
    """Get the user's collection observation summary."""
    obs_summaries = models.Collection.get_all_visit_summaries(collection_id)

    if not obs_summaries:
        raise ResourceNotFound("Collection not found.")
    
    return jsonify({
        "success": True,
        "summaries": obs_summaries,
    }), 201

# Method to calculate average time between events
@api.route("/collections/time_between_visits/<int:collection_id>")
@jwt_required
def get_collection_time_between_visits(collection_id):
    query_by = request.args.get("query_by")

    # only count subjects with first/last observations for these variables
    obs_var_ids = request.args.get('obs_var_ids')

    # single first/last visit for all variables
    visit1 = request.args.get("visit1")
    visit2 = request.args.get("visit2")
    
    # distinct first/last visit for each variable
    fv = request.args.get("first_visits")
    lv = request.args.get("last_visits")
    ovl = obs_var_ids.split(",")

    if visit1 is not None:
        avg_times = models.Collection.get_avg_time_between_visits(collection_id, query_by, visit1, visit2, ovl)
        return jsonify({
            "success": True,
            "obs_var_ids": obs_var_ids,
            "visit1": visit1,
            "visit2": visit2,
            "query_by": query_by,
            "times": avg_times,
        }), 201
    else:
        fvl = fv.split(",")
        lvl = lv.split(",")

        avg_times = models.Collection.get_avg_time_between_visits(collection_id, query_by, fvl, lvl, ovl)

        return jsonify({
            "success": True,
            "obs_var_ids": obs_var_ids,
            "first_visits": fv,
            "last_visits": lv,
            "query_by": query_by,
            "times": avg_times,
        }), 201
