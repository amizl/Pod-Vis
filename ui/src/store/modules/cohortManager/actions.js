import axios from 'axios';
import { nest } from 'd3-collection';
import { ErrorNotification } from '@/store/modules/notifications/notifications';
import { actions, mutations, state as stateTypes } from './types';
import { makeHierarchy } from './helpers';

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
      const notification = new ErrorNotification(response.data.error);
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
      let wideData = nest()
        // Group by subject ID
        .key(d => d.subject_id)
        // This is very convoluted...ideally we want the
        // server to massage the data into the format we need
        // and send it back...however there was issues using pandas
        // and getting nested data for the observations. May need to
        // revisit later on. Here we are are tranforming each subject
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
        .entries(data) // tell it what data to process
        .map(d => {
          // pull out only the values
          return d.value;
        });

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
  [actions.ADD_OUTPUT_VARIABLE]({ commit }, inputVariable) {
    commit(mutations.ADD_OUTPUT_VARIABLE, inputVariable);
  },
  [actions.SET_OUTPUT_VARIABLES]({ commit }, newOutputVariables) {
    commit(mutations.SET_OUTPUT_VARIABLES, newOutputVariables);
  },
  [actions.ADD_DIMENSION]({ commit }, dimension) {
    commit(mutations.ADD_DIMENSION, dimension);
  },
  [actions.ADD_FILTER]({ commit }, { dimension, filter }) {
    commit(mutations.ADD_FILTER, { dimension, filter });
    commit(mutations.UPDATE_FILTERED_DATA);
  },
  [actions.CLEAR_FILTER]({ commit }, { dimension }) {
    commit(mutations.CLEAR_FILTER, { dimension });
    commit(mutations.UPDATE_FILTERED_DATA);
  },
};
