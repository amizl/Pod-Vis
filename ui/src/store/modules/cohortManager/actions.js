import axios from 'axios';
import { nest } from 'd3-collection';
import {
  ErrorNotification,
  SuccessNotification,
} from '@/store/modules/notifications/notifications';
import {
  makeHierarchy,
  getInputVariablesFromQueries,
  getCohortSubjectIds,
} from '@/utils/helpers';
import {
  actions,
  getters as getterTypes,
  mutations,
  state as stateTypes,
} from './types';

export default {
  async [actions.FETCH_COHORTS]({ commit, dispatch }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/cohorts');
      commit(mutations.SET_COHORTS, data.cohorts);
    } catch (err) {
      // TODO
    } finally {
      commit(mutations.SET_LOADING, false);
    }
    dispatch(actions.SET_COHORT_SUBJECTS);
  },
  [actions.SET_COHORT_SUBJECTS]({ state }) {
    const { cohorts, collection, data } = state;
    if (
      typeof collection === 'undefined' ||
      typeof cohorts === 'undefined' ||
      typeof data === 'undefined' ||
      data.length === 0
    ) {
      return;
    }
    // compute subjects in each cohort
    cohorts.forEach(c => {
      if (c.collection_id === collection.id) {
        const subjIds = getCohortSubjectIds(data, c);
        c.subject_ids = subjIds;
      }
    });
  },
  async [actions.FETCH_COLLECTION]({ commit, dispatch }, collectionId) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        `/api/collections/${collectionId}?include=studies&include=variables&include=cohorts`
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
      data.collection.observation_variables_list =
        data.collection.observation_variables;

      data.collection.has_visits_set = true;
      data.collection.observation_variables_list.forEach(ov => {
        if (
          (ov.first_visit_event == null && ov.first_visit_num == null) ||
          (ov.last_visit_event == null && ov.last_visit_num == null)
        ) {
          data.collection.has_visits_set = false;
        }
      });

      observationVariables.forEach(observationVariable => {
        observationVariable.children.forEach(child => {
          child.type = 'observation';
          if (data.collection.is_longitudinal) {
            child.is_longitudinal = true;
            var children = [
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
            ];
            if (child.data_category == 'Continuous') {
              children.push(
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
                }
              );
            }
            child.children = children;
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
      if ('response' in e && 'data' in e.response) {
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
      commit(mutations.SET_DATA, wideData);
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
  [actions.CLEAR_ALL_FILTERS]({ commit, dispatch, state }) {
    var dimensions = Object.keys(state[stateTypes.DIMENSIONS]);
    commit(mutations.RESET_QUERIES);
    dimensions.forEach(dimension => {
      commit(mutations.CLEAR_FILTER, { dimension });
    });
    commit(mutations.UPDATE_FILTERED_DATA);
    dispatch(actions.ANALYZE_FILTERED);
  },
  async [actions.ANALYZE_FILTERED]({ commit, dispatch, state }) {
    const { filteredData } = state;
    let { unfilteredData, outputVariables } = state;
    const collection = state[stateTypes.COLLECTION];
    const comparisonMeasure = state[stateTypes.COMPARISON_MEASURE];
    // TODO - this mapping is already performed on the server side (more than once)
    const m2f = {
      'First Visit': 'firstVisit',
      'Last Visit': 'lastVisit',
      Change: 'change',
      'Rate of Change': 'roc',
    };
    const comparisonField = m2f[comparisonMeasure];

    // selected cohort is empty or equal to study population - nothing to compare
    if (
      filteredData.length === unfilteredData.length ||
      filteredData.length == 0
    ) {
      // increment requestnum to ensure any previously-submitted request is ignored
      var cb = function() {};
      commit(mutations.INCREMENT_PVALS_REQUEST_NUM, { callback: cb });
      // Nothing is filtered
      commit(mutations.SET_PVALS_REQUEST_STATUS, null);
      commit(mutations.SET_PVALS, []);
    }
    // selected cohort is strict subset of study population
    else {
      //      console.log("analyzeFiltered called at " + new Date().getTime() + " with requestNum=" + (state[stateTypes.PVALS_REQUEST_NUM]+1));
      commit(mutations.SET_PVALS_REQUEST_STATUS, 'loading');

      // Remove subjects within our filtered data sets from our unfiltered so
      // we can have separate samples
      var filteredDataSubjIds = {};
      filteredData.map(d => {
        filteredDataSubjIds[d.subject_id] = 1;
      });
      var numFilteredSubjIds = Object.keys(filteredDataSubjIds).length;

      var unfilteredDataSubjIds = {};
      unfilteredData.map(d => {
        unfilteredDataSubjIds[d.subject_id] = 1;
      });
      var numUnfilteredSubjIds = Object.keys(unfilteredDataSubjIds).length;

      var remainderData = unfilteredData.filter(
        data => !(data.subject_id in filteredDataSubjIds)
      );
      var remainderDataSubjIds = {};
      remainderData.map(d => {
        remainderDataSubjIds[d.subject_id] = 1;
      });
      var numRemainderSubjIds = Object.keys(remainderDataSubjIds).length;

      // sanity check - unfiltered subjects should be split into two distinct groups
      if (
        numRemainderSubjIds + numFilteredSubjIds !== numUnfilteredSubjIds ||
        numRemainderSubjIds == numUnfilteredSubjIds
      ) {
        const notification = new ErrorNotification(
          'ERROR - data filtering failed numFiltered=' +
            numFilteredSubjIds +
            ' numUnfiltered=' +
            numUnfilteredSubjIds +
            ' numRemainder=' +
            numRemainderSubjIds
        );
        dispatch(notification.dispatch, notification, { root: true });
      }

      // pass _all_ observation variables, not just the selected ones
      const outputVars = [];
      collection.observation_variables.forEach(v => {
        v.children.forEach(c => {
          outputVars.push(c);
        });
      });
      outputVariables = outputVars;

      // TODO - cancel superseded pending requests instead of just ignoring them
      cb = async function(reqnum) {
        // wait PVALS_REQUEST_DELAY_SECS before sending request to ensure the filtered data isn't still changing
        setTimeout(async function() {
          if (state[stateTypes.PVALS_REQUEST_NUM] > reqnum) {
            //		  console.log("reqnum " + reqnum + " is no longer current, skipping request");
            return;
          }
          //	      console.log("reqnum " + reqnum + " is still current, sending request");

          try {
            const { data } = await axios.post(`/api/compute-mannwhitneyu`, {
              comparisonField: comparisonField,
              filteredData: filteredData,
              unfilteredData: remainderData,
              outputVariables: outputVariables,
            });

            if (state[stateTypes.PVALS_REQUEST_NUM] > reqnum) {
              //		      console.log("request " + reqnum + " is no longer current, ignoring return value");
            } else {
              //		      console.log("accepting request " + reqnum);
              commit(mutations.SET_PVALS_REQUEST_STATUS, 'loaded');
              commit(mutations.SET_PVALS, data.pvals);
            }
          } catch ({ response }) {
            const notification = new ErrorNotification(response.data.error);
            dispatch(notification.dispatch, notification, { root: true });
          }
        }, state[stateTypes.PVALS_REQUEST_DELAY_SECS] * 1000);
      };

      commit(mutations.INCREMENT_PVALS_REQUEST_NUM, { callback: cb });
    }
  },
  async [actions.ANALYZE_COHORTS]({ commit, dispatch, state }, cohorts) {
    let { outputVariables } = state;
    const collection = state[stateTypes.COLLECTION];
    const comparisonMeasure = state[stateTypes.COMPARISON_MEASURE];
    // TODO - this mapping is already performed on the server side (more than once)
    const m2f = {
      'First Visit': 'firstVisit',
      'Last Visit': 'lastVisit',
      Change: 'change',
      'Rate of Change': 'roc',
    };
    const comparisonField = m2f[comparisonMeasure];
    // nothing to compare
    if (cohorts.length == 0) {
      // increment requestnum to ensure any previously-submitted request is ignored
      var cb = function() {};
      commit(mutations.INCREMENT_ANOVA_PVALS_REQUEST_NUM, { callback: cb });
      // Nothing is filtered
      commit(mutations.SET_ANOVA_PVALS_REQUEST_STATUS, null);
      commit(mutations.SET_ANOVA_PVALS, []);
    } else {
      commit(mutations.SET_ANOVA_PVALS_REQUEST_STATUS, 'loading');
      // pass _all_ observation variables, not just the selected ones
      const outputVars = [];
      collection.observation_variables.forEach(v => {
        v.children.forEach(c => {
          outputVars.push(c);
        });
      });
      outputVariables = outputVars;

      const groups = cohorts.map(c => c.data);
      const numGroups = groups.length;

      // TODO - cancel superseded pending requests instead of just ignoring them
      cb = async function(reqnum) {
        // wait ANOVA_PVALS_REQUEST_DELAY_SECS before sending request to ensure the filtered data isn't still changing
        setTimeout(async function() {
          if (state[stateTypes.ANOVA_PVALS_REQUEST_NUM] > reqnum) {
            return;
          }
          try {
            const input = {
              numGroups,
              groups,
              outputVariables,
              comparisonField,
            };

            const { data } = await axios.post(`/api/compute-anova`, input);

            if (state[stateTypes.ANOVA_PVALS_REQUEST_NUM] > reqnum) {
              //		      console.log("request " + reqnum + " is no longer current, ignoring return value");
            } else {
              //		      console.log("accepting request " + reqnum);
              commit(mutations.SET_ANOVA_PVALS_REQUEST_STATUS, 'loaded');
              commit(mutations.SET_ANOVA_PVALS, data.pvals);
            }
          } catch ({ response }) {
            const notification = new ErrorNotification(response.data.error);
            dispatch(notification.dispatch, notification, { root: true });
          }
        }, state[stateTypes.ANOVA_PVALS_REQUEST_DELAY_SECS] * 1000);
      };
      commit(mutations.INCREMENT_ANOVA_PVALS_REQUEST_NUM, { callback: cb });
    }
  },
  async [actions.SAVE_COHORT]({ commit, dispatch }, args) {
    const {
      name,
      collection,
      queries,
      inputVariables,
      outputVariables,
      subjectIds,
    } = args;

    const queriesMappedToVariables = getInputVariablesFromQueries(
      queries,
      inputVariables
    );

    try {
      const { data } = await axios.post('/api/cohorts', {
        queries: queriesMappedToVariables,
        input_variables: inputVariables,
        output_variables: outputVariables,
        cohort_subjects: subjectIds,
        cohort_name: name,
        collection_id: collection.id,
      });
      data.cohort.subject_ids = subjectIds;
      commit(mutations.ADD_COHORT, data.cohort);
      const notification = new SuccessNotification(`Study group saved`);
      dispatch(notification.dispatch, notification, { root: true });
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    }
  },
  async [actions.SAVE_SELECTED_COHORT]({ dispatch, state }, { cohortName }) {
    const {
      collection,
      queries,
      inputVariables,
      outputVariables,
      filteredData,
    } = state;
    const subjectIds = filteredData.map(subject => subject.subject_id);
    var args = {
      name: cohortName,
      collection: collection,
      queries: queries,
      inputVariables: inputVariables,
      outputVariables: outputVariables,
      subjectIds: subjectIds,
    };

    dispatch(actions.SAVE_COHORT, args);
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
  async [actions.SET_COHORT_NO_RESET]({ commit }, cohort) {
    commit(mutations.SET_COHORT, cohort);
  },
  async [actions.DELETE_COHORT]({ dispatch }, cohortId) {
    try {
      await axios.delete(`/api/cohorts/${cohortId}`);
      dispatch(actions.REMOVE_COHORT, cohortId);
      const notification = new SuccessNotification(`Successfully deleted`);
      dispatch(notification.dispatch, notification, { root: true });
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    }
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
  [actions.SET_COMPARISON_MEASURE]({ commit, dispatch }, measure) {
    commit(mutations.SET_COMPARISON_MEASURE, measure);
    dispatch(actions.ANALYZE_FILTERED);
  },
  [actions.SET_USE_LONG_SCALE_NAMES]({ commit }, useLong) {
    commit(mutations.SET_USE_LONG_SCALE_NAMES, useLong);
  },
  [actions.SET_HELP_MODE]({ commit }, helpMode) {
    commit(mutations.SET_HELP_MODE, helpMode);
  },
  [actions.SET_SORT]({ commit }, sort) {
    commit(mutations.SET_SORT, sort);
  },
};
