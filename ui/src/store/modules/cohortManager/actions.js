import axios from 'axios';
import { nest } from 'd3-collection';
import {
  ErrorNotification,
  SuccessNotification,
} from '@/store/modules/notifications/notifications';
import { makeHierarchy, getInputVariablesFromQueries } from '@/utils/helpers';
import {
  actions,
  getters as getterTypes,
  mutations,
  state as stateTypes,
} from './types';

export default {
  async [actions.FETCH_COHORTS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/cohorts');
      commit(mutations.SET_COHORTS, data.cohorts);
    } catch (err) {
      // TODO
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  async [actions.FETCH_COLLECTION]({ commit, dispatch }, collectionId) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        `/api/collections/${collectionId}?include=studies&include=variables`
      );

      // massage collection data... here
      const subjectVariables = makeHierarchy(data.collection.subject_variables);

      subjectVariables.forEach(subjectVariable => {
        if (subjectVariable.children) {
          subjectVariable.children.forEach(child => {
            child.type = 'subject';
          });
        }
	  if (subjectVariable.label === 'Dataset') {
	      subjectVariable.type = 'subject';
	  }
      });

      // determine whether this is longitudinal or cross-sectional data
      data.collection.is_longitudinal = true;
      data.collection.studies.forEach(s => {
        if (s.study.longitudinal === 0) data.collection.is_longitudinal = false;
      });

      const observationVariables = makeHierarchy(
        data.collection.observation_variables
      );

      // TODO:
      // These fields are hard-coded and will inevitably need to be changed.
      // For example, firstVisit and lastVisit are stored in the database as
      //  left_y_axis and right_y_axis when queries are saved. This is because
      //  eventually we want to allow the user to specify the visit number rather
      //  than hard-coding first and last.
      observationVariables.forEach(observationVariable => {
        observationVariable.children.forEach(child => {
          child.type = 'observation';
          if (data.collection.is_longitudinal) {
            child.is_longitudinal = true;
            child.children = [
              {
                ...child,
                id: `firstVisit-${child.id}`,
                parentID: child.id,
                parentLabel: child.label,
                label: 'First Visit',
              },
              {
                ...child,
                id: `lastVisit-${child.id}`,
                parentID: child.id,
                parentLabel: child.label,
                label: 'Last Visit',
              },
              {
                ...child,
                id: `change-${child.id}`,
                parentID: child.id,
                parentLabel: child.label,
                label: 'Change',
              },
              {
                ...child,
                id: `roc-${child.id}`,
                parentID: child.id,
                parentLabel: child.label,
                label: 'Rate of Change',
              },
            ];
          } else {
            child.is_longitudinal = false;
          }
        });
      });

      data.collection.subject_variables = subjectVariables;
      data.collection.observation_variables = observationVariables;
      commit(mutations.SET_COLLECTION, data.collection);
    } catch (e) {
      // Something went wrong...
      // user didn't have access to collection? collection not found?
      // Display notification via notifcation snackbar? Reroute? Display msg in cohort manager?
      // TODO...

      // Currently displays error message.
	let err = e;
	if (('response' in e) && ('data' in e.response)) {
	    err = e.response.data.error;
	}
	const notification = new ErrorNotification(err);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  async [actions.FETCH_DATA]({ commit, dispatch, state }) {
    commit(mutations.SET_LOADING, true);
    const collection = state[stateTypes.COLLECTION];
    try {
      const response = await axios.get(
        `/api/cohort-manager?collection=${collection.id}`
      );

      const data = JSON.parse(response.data.data);

      // Massage data into a format we will use...
      // [{
      //     Sex: 'male',
      //     Race: 'white',
      //     ...
      //     1: {
      //       "roc": ...,
      //       "firstVisit": ...,
      //       "lastVisit": ...
      //     }
      // }]
      // TODO - "Use d3-array’s group and rollup instead of d3-collection’s nest." (which is deprecated)
      const wideData = nest()
        // Group by subject ID
        .key(d => d.subject_id)
        // This is very convoluted...ideally we want the
        // server to massage the data into the format we need
        // and send it back...however there was issues using pandas
        // and getting nested data for the observations. May need to
        // revisit later on. Here we are are transforming each subject
        // record so that we nest its outcome measure with firstVisit,
        // lastVisit, and rate of change. We then want to reduce this
        // so we have a single object with keys of all its outcome measures.
        // This can be considered moving from "long to wide".
        .rollup(values =>
          values
            .map(d => {
              const { observation, change, roc, min, max, value, ...rest } = d;
              return {
                [observation]: {
                  value,
                  change,
                  roc,
                  firstVisit: min,
                  lastVisit: max,
                },
                ...rest,
              };
            })
            .reduce((prev, curr) => ({ ...prev, ...curr }), {})
        )
        .entries(data.data) // tell it what data to process
        .map(
          d =>
            // pull out only the values
            d.value
        );

      commit(mutations.INITIALIZE_CROSS_FILTER, wideData);
      commit(mutations.UPDATE_FILTERED_DATA);
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  [actions.ADD_INPUT_VARIABLE]({ commit }, inputVariable) {
    commit(mutations.ADD_INPUT_VARIABLE, inputVariable);
  },
  [actions.REMOVE_INPUT_VARIABLE]({ commit }, inputVariable) {
    commit(mutations.REMOVE_INPUT_VARIABLE, inputVariable);
  },
  [actions.SET_INPUT_VARIABLES]({ commit }, newInputVariables) {
    commit(mutations.SET_INPUT_VARIABLES, newInputVariables);
  },
  [actions.REMOVE_OUTPUT_VARIABLE]({ commit }, outputVariable) {
    commit(mutations.REMOVE_OUTPUT_VARIABLE, outputVariable);
  },
  [actions.ADD_OUTPUT_VARIABLE]({ commit }, outputVariable) {
    commit(mutations.ADD_OUTPUT_VARIABLE, outputVariable);
  },
  [actions.SET_OUTPUT_VARIABLES]({ commit, dispatch }, newOutputVariables) {
    commit(mutations.SET_OUTPUT_VARIABLES, newOutputVariables);
    dispatch(actions.ANALYZE_FILTERED);
  },
  [actions.ADD_DIMENSION]({ commit }, dimension) {
    commit(mutations.ADD_DIMENSION, dimension);
  },
  [actions.ADD_FILTER]({ commit, dispatch }, { dimension, filter, query }) {
    commit(mutations.SET_QUERY, { dimension, query });
    commit(mutations.ADD_FILTER, { dimension, filter });
    commit(mutations.UPDATE_FILTERED_DATA);

    dispatch(actions.ANALYZE_FILTERED);
  },
  [actions.CLEAR_FILTER]({ commit, dispatch }, { dimension }) {
    commit(mutations.CLEAR_QUERY, dimension);
    commit(mutations.CLEAR_FILTER, { dimension });
    commit(mutations.UPDATE_FILTERED_DATA);

    dispatch(actions.ANALYZE_FILTERED);
  },
  [actions.CLEAR_ALL_FILTERS]({ dispatch, state }) {
    Object.keys(state[stateTypes.DIMENSIONS]).forEach(dimension => {
      dispatch(actions.CLEAR_FILTER, { dimension });
    });
  },
  async [actions.ANALYZE_FILTERED]({ commit, dispatch, state }) {
    const { filteredData } = state;
    let { unfilteredData, outputVariables } = state;
    const collection = state[stateTypes.COLLECTION];

    // TODO - run another test instead
    if (!collection.is_longitudinal) {
      //	console.log("cross-sectional dataset detected, not running Mann-Whitney rank test");
    } else if (filteredData.length === unfilteredData.length) {
      // increment requestnum to ensure any previously-submitted request is ignored
      var cb = function(reqnum) {};
      commit(mutations.INCREMENT_REQUEST_NUM, { callback: cb });
      // Nothing is filtered
      commit(mutations.SET_PVALS, []);
    } else {
      // Remove subjects within our filtered data sets from our unfiltered so
      // we can have separate samples
      unfilteredData = unfilteredData.filter(
        data =>
          !filteredData
            .map(({ subjectId }) => subjectId)
            .includes(data.subject_id)
      );

      // pass _all_ observation variables, not just the selected ones
      const outputVars = [];
      collection.observation_variables.forEach(v => {
        v.children.forEach(c => {
          outputVars.push(c);
        });
      });
      outputVariables = outputVars;

      // TODO - actually cancel superseded pending requests instead of just ignoring them
      var cb = async function(reqnum) {
        try {
          const { data } = await axios.post(`/api/compute-mannwhitneyu`, {
            filteredData,
            unfilteredData,
            outputVariables,
          });

          if (state[stateTypes.REQUEST_NUM] > reqnum) {
            //		console.log("request " + reqnum + " is no longer current, ignoring return value");
          } else {
            commit(mutations.SET_PVALS, data.pvals);
          }
        } catch ({ response }) {
          const notification = new ErrorNotification(response.data.error);
          dispatch(notification.dispatch, notification, { root: true });
        }
      };

      commit(mutations.INCREMENT_REQUEST_NUM, { callback: cb });
    }
  },
  async [actions.SAVE_COHORT]({ commit, dispatch, state }, { cohortName }) {
    const {
      collection,
      queries,
      inputVariables,
      outputVariables,
      filteredData,
    } = state;

    const subjectsInCohort = filteredData.map(subject => subject.subject_id);

    const queriesMappedToVariables = getInputVariablesFromQueries(
      queries,
      inputVariables
    );

    // queriesMappedToVariables
    //   .filter(query => query.variable.type === 'study')
    //   .forEach(query => {
    //     console.log(query);
    //     const { studies } = collection;
    //     const queryStudies = query.query.map(({ value }) => {
    //       const study = studies.find(({ study }) => study.study_name === value);
    //       return study;
    //     });

    //     query.variable.id = study.study.id;
    //   });

    // console.log(queriesMappedToVariables);
    try {
      const { data } = await axios.post('/api/cohorts', {
        queries: queriesMappedToVariables,
        input_variables: inputVariables,
        output_variables: outputVariables,
        cohort_subjects: subjectsInCohort,
        cohort_name: cohortName,
        collection_id: collection.id,
      });
      commit(mutations.ADD_COHORT, data.cohort);

      // Clean up data... may want to put this is in its own dispatch action call.
      dispatch(actions.SET_COHORT, { id: null });
      commit(mutations.RESET_DIMENSIONS);
      commit(mutations.RESET_QUERIES);
      commit(mutations.RESET_PVALS);
      const notification = new SuccessNotification(`Cohort saved`);
      dispatch(notification.dispatch, notification, { root: true });
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    }
  },
  async [actions.SET_COHORT]({ commit, dispatch, getters }, cohort) {
    commit(mutations.RESET_PVALS);
    commit(mutations.RESET_OUTPUT_VARIABLES);
    commit(mutations.RESET_INPUT_VARIABLES);
    commit(mutations.SET_COHORT, cohort);

    //    const studyInputVariables =
    //      getters[getterTypes.FIND_COHORT_STUDY_INPUT_VARIABLES];
    const subjectInputVariables =
      getters[getterTypes.FIND_COHORT_SUBJECT_INPUT_VARIABLES];
    const observationInputVariables =
      getters[getterTypes.FIND_COHORT_OBSERVATION_INPUT_VARIABLES];
    const outputVariables =
      getters[getterTypes.FIND_COHORT_OBSERVATION_OUTPUT_VARIABLES];
    dispatch(actions.CLEAR_ALL_FILTERS);
    dispatch(actions.SET_INPUT_VARIABLES, [
      //      ...studyInputVariables,
      ...subjectInputVariables,
      ...observationInputVariables,
    ]);
    dispatch(actions.SET_OUTPUT_VARIABLES, outputVariables);
  },
  async [actions.DELETE_SELECTED_COHORT]({ state, dispatch }) {
    try {
      const { cohort } = state;
      await axios.delete(`/api/cohorts/${cohort.id}`);

      dispatch(actions.SET_COHORT, { id: null });
      dispatch(actions.REMOVE_COHORT, cohort.id);

      const notification = new SuccessNotification(`Successfully deleted`);
      dispatch(notification.dispatch, notification, { root: true });
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    }
  },
  async [actions.REMOVE_COHORT]({ commit }, cohortID) {
    commit(mutations.REMOVE_COHORT, cohortID);
  },
  [actions.RESET_ALL_STORE_DATA]({ commit }) {
    commit(mutations.RESET_COHORTS);
    commit(mutations.RESET_IS_LOADING);
    commit(mutations.RESET_COLLECTION);
    commit(mutations.RESET_UNFILTERED_DATA);
    commit(mutations.RESET_FILTERED_DATA);
    commit(mutations.RESET_INPUT_VARIABLES);
    commit(mutations.RESET_OUTPUT_VARIABLES);
    commit(mutations.RESET_CROSS_FILTER);
    commit(mutations.RESET_DIMENSIONS);
    commit(mutations.RESET_PVALS);
    commit(mutations.RESET_QUERIES);
  },
  [actions.SET_PVAL_THRESHOLD]({ commit }, threshold) {
    commit(mutations.SET_PVAL_THRESHOLD, threshold);
  },
  [actions.RESET_PVAL_THRESHOLD]({ commit }) {
    commit(mutations.SET_PVAL_THRESHOLD);
  },
  [actions.SET_HIGHLIGHTED_SUBSET]({ commit }, subset) {
    commit(mutations.SET_HIGHLIGHTED_SUBSET, subset);
  },
  [actions.RESET_HIGHLIGHTED_SUBSET]({ commit }) {
    commit(mutations.RESET_HIGHLIGHTED_SUBSET);
  },
};
