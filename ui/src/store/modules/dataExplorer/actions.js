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
        .entries(data['data']) // tell it what data to process
        .map(d => {
          // pull out only the values
          return d.value;
        });

      commit(mutations.SET_DATA, wideData);
      commit(mutations.SET_RAW_DATA, data['raw_data']);
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  [actions.SET_OUTCOME_VARIABLES]({ commit, dispatch }, outcomeVariables) {
    commit(mutations.SET_OUTCOME_VARIABLES, outcomeVariables);
  },
  [actions.SET_DETAILED_VIEW]({ commit }, detailedView) {
    commit(mutations.SET_DETAILED_VIEW, detailedView);
  },
  async [actions.FETCH_COHORTS]({ commit, dispatch, state }) {
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
    dispatch(actions.ANALYZE_COHORTS);
  },
  [actions.SET_VISIBLE_COHORTS]({ commit }, cohorts) {
    commit(mutations.SET_VISIBLE_COHORTS, cohorts);
  },
  async [actions.ANALYZE_COHORTS]({ commit, dispatch, state }) {
    let { cohorts, data, outputVariables } = state;
    const collection = state[stateTypes.COLLECTION];

      // need cohorts, collection, and output vars
      if ((typeof collection === 'undefined') || (typeof collection.observation_variables === 'undefined') || (typeof cohorts === 'undefined')) {
	commit(mutations.SET_ANOVA_PVALS, []);
	return;
    }
      
    // create group of samples for each cohort:
    let groups = [];
    cohorts.forEach(function(c) {
      if (c.collection_id === collection.id) {
        let subjids = [];
        c.subject_ids.forEach(function(sid) { subjids[sid] = 1; });
        let cohort_data = data.filter(d => d.subject_id in subjids);	  
        groups.push(cohort_data);
      }
    });
    let numGroups = groups.length;

    // pass _all_ observation variables, not just the selected ones
    var output_vars = [];
    collection.observation_variables.forEach(function(v) {
      v.children.forEach(function(c) {
        output_vars.push(c);
      });
    });
    outputVariables = output_vars;

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
  [actions.SET_COHORT_SUBJECTS]({ commit, dispatch, state }) {
      let { cohorts, collection, data } = state;
      if ((typeof(collection) === 'undefined') || (typeof(cohorts) === 'undefined')
	  || (typeof(data) === 'undefined') || (data.length === 0)) {
	  return;
      }
      
      // compute subjects in each cohort
      cohorts.forEach(function(c) {
          if (c.collection_id === collection.id) {
	    let subj_ids = getCohortSubjectIds(data, c);
            c.subject_ids = subj_ids;
	  }
      });
  },
};
