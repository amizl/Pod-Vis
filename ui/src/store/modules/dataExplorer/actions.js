import axios from 'axios';
import { nest } from 'd3-collection';
import { ErrorNotification } from '@/store/modules/notifications/notifications';
import { makeHierarchy, getCohortSubjectIds } from '@/utils/helpers';
import { actions, mutations, state as stateTypes } from './types';

export default {
  async [actions.FETCH_COLLECTION]({ commit, dispatch }, collectionId) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        `/api/collections/${collectionId}?include=studies&include=variables&include=cohorts`
      );
      // massage collection data... here

      var c = data.collection;
      c.date_generated_epoch = new Date(c.date_generated).getTime();
      c.has_visits_set = true;
      c.observation_variables.forEach(v => {
        if (
          (v.first_visit_event == null && v.first_visit_num == null) ||
          (v.last_visit_event == null && v.last_visit_num == null)
        ) {
          c.has_visits_set = false;
        }
      });

      const subjectVariables = makeHierarchy(data.collection.subject_variables);

      subjectVariables.forEach(subjectVariable => {
        subjectVariable.children.forEach(child => {
          child.type = 'subject';
        });
      });

      const observationVariables = makeHierarchy(
        data.collection.observation_variables
      );

      data.collection.observation_variables_list =
        data.collection.observation_variables;
      data.collection.subject_variables = subjectVariables;
      data.collection.observation_variables = observationVariables;
      commit(mutations.SET_COLLECTION, data.collection);
      dispatch(actions.SET_COHORT_SUBJECTS);
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
      const wideData = nest()
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
        .rollup(values =>
          values
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
            .reduce((prev, curr) => ({ ...prev, ...curr }), {})
        )
        .entries(data.data) // tell it what data to process
        .map(
          d =>
            // pull out only the values
            d.value
        );

      commit(mutations.SET_DATA, wideData);
      commit(mutations.SET_RAW_DATA, data.raw_data);
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  [actions.SET_OUTCOME_VARIABLES]({ commit }, outcomeVariables) {
    commit(mutations.SET_OUTCOME_VARIABLES, outcomeVariables);
  },
  [actions.SET_DETAILED_VIEW]({ commit }, detailedView) {
    commit(mutations.SET_DETAILED_VIEW, detailedView);
  },
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
  [actions.SET_VISIBLE_COHORTS]({ commit }, cohorts) {
    commit(mutations.SET_VISIBLE_COHORTS, cohorts);
  },
  async [actions.ANALYZE_COHORTS]({ commit, dispatch, state }, cohorts) {
    const { data } = state;
    let { outputVariables } = state;
    const collection = state[stateTypes.COLLECTION];

    // need cohorts, collection, and output vars
    if (
      typeof collection === 'undefined' ||
      typeof collection.observation_variables === 'undefined' ||
      typeof cohorts === 'undefined'
    ) {
      commit(mutations.SET_ANOVA_PVALS, []);
      return;
    }

    // create group of samples for each cohort:
    const groups = [];
    cohorts.forEach(c => {
      if (c.collection_id === collection.id) {
        const subjids = [];
        c.subject_ids.forEach(sid => {
          subjids[sid] = 1;
        });
        const cohortData = data.filter(d => d.subject_id in subjids);
        groups.push(cohortData);
      }
    });
    const numGroups = groups.length;

    // pass _all_ observation variables, not just the selected ones
    const outputVars = [];
    collection.observation_variables.forEach(v => {
      v.children.forEach(c => {
        outputVars.push(c);
      });
    });
    outputVariables = outputVars;

    try {
      const { data } = await axios.post(`/api/compute-anova`, {
        numGroups,
        groups,
        outputVariables,
      });
      commit(mutations.SET_ANOVA_PVALS, data.pvals);
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    }
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
};
