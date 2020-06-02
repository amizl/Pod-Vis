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
        subjectVariable.children.forEach(child => (child['type'] = 'subject'));
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
          child['type'] = 'observation';
          child['children'] = [
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
        });
      });

      data.collection.subject_variables = subjectVariables;
      data.collection.observation_variables = observationVariables;
      commit(mutations.SET_COLLECTION, data.collection);
    } catch ({ response }) {
      // Something went wrong...
      // user didn't have access to collection? collection not found?
      // Display notification via notifcation snackbar? Reroute? Display msg in cohort manager?
      // TODO...

      // Currently displays error message.
      const notification = new ErrorNotification(response);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  async [actions.FETCH_COLLECTION_SUMMARY_BY_EVENT](
    { commit, dispatch },
    collectionId
  ) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        `/api/collections/obs_summary_by_event/${collectionId}`
      );
      // massage collection observation summary data... here
      commit(mutations.SET_COLLECTION_SUMMARY, data);
    } catch ({ response }) {
      // Something went wrong...
      // user didn't have access to collection? collection not found?
      // Display notification via notifcation snackbar? Reroute? Display msg in cohort manager?
      // TODO...

      // Currently displays error message.
      const notification = new ErrorNotification(response);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  async [actions.FETCH_DATA]({ commit, dispatch, state }) {
    commit(mutations.SET_LOADING, true);
    const collection = state[stateTypes.COLLECTION];
    try {
      let response = await axios.get(
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
      let wideData = nest()
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
        .rollup(values => {
          return values
            .map(d => {
              const { observation, change, roc, min, max, ...rest } = d;
              return {
                [observation]: {
                  change,
                  roc,
                  firstVisit: min,
                  lastVisit: max,
                },
                ...rest,
              };
            })
            .reduce((prev, curr) => {
              return { ...prev, ...curr };
            }, {});
        })
        .entries(data['data']) // tell it what data to process
        .map(d => {
          // pull out only the values
          return d.value;
        });

      commit(mutations.INITIALIZE_CROSS_FILTER, wideData);
      commit(mutations.UPDATE_FILTERED_DATA);
    } catch ({ response }) {
      const notification = new ErrorNotification(response);
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
    let { filteredData, unfilteredData, outputVariables } = state;
    if (filteredData.length == unfilteredData.length) {
      // Nothing is filtered
      commit(mutations.SET_PVALS, []);
    } else {
      // Remove subjects within our filtered data sets from our unfiltered so
      // we can have separate samples
      unfilteredData = unfilteredData.filter(data => {
        return !filteredData
          .map(({ subject_id }) => subject_id)
          .includes(data.subject_id);
      });

      // pass _all_ observation variables, not just the selected ones
      const collection = state[stateTypes.COLLECTION];
      var output_vars = [];
      collection.observation_variables.forEach(function(v) {
        v.children.forEach(function(c) {
          output_vars.push(c);
        });
      });
      outputVariables = output_vars;
	
      try {
        const { data } = await axios.post(`/api/compute-mannwhitneyu`, {
          filteredData,
          unfilteredData,
          outputVariables,
        });

        commit(mutations.SET_PVALS, data.pvals);
      } catch ({ response }) {
        const notification = new ErrorNotification(response.data.error);
        dispatch(notification.dispatch, notification, { root: true });
      }
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
  [actions.SET_PVAL_THRESHOLD]({ commit }, threshold ) {
    commit(mutations.SET_PVAL_THRESHOLD, threshold);
  },
  [actions.RESET_PVAL_THRESHOLD]({ commit }) {
    commit(mutations.SET_PVAL_THRESHOLD);
  },
  [actions.SET_HIGHLIGHTED_SUBSET]({ commit }, subset ) {
    commit(mutations.SET_HIGHLIGHTED_SUBSET, subset);
  },
  [actions.RESET_HIGHLIGHTED_SUBSET]({ commit }) {
    commit(mutations.RESET_HIGHLIGHTED_SUBSET);
  },
  [actions.SET_FIRST_VISIT]({ commit }, newFirstVisit) {
    commit(mutations.SET_FIRST_VISIT, newFirstVisit);
  },
  [actions.SET_LAST_VISIT]({ commit }, newLastVisit) {
    commit(mutations.SET_LAST_VISIT, newLastVisit);
  },
};
