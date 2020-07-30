import axios from 'axios';
import { ErrorNotification } from '@/store/modules/notifications/notifications';
import { actions, mutations } from './types';

export default {
  [actions.SET_SELECTED_COHORTS]({ commit }, cohorts) {
    commit(mutations.SET_SELECTED_COHORTS, cohorts);
  },

  [actions.SET_SELECTED_OUTCOME_VARIABLE]({ commit }, outcomeVariable) {
    commit(mutations.SET_SELECTED_OUTCOME_VARIABLE, outcomeVariable);
  },

  async [actions.ANALYZE_COHORTS](
    { commit, dispatch },
    { collection, cohorts, data }
  ) {
    // need cohorts, collection, and output vars
    if (
      typeof collection === 'undefined' ||
      typeof collection.observation_variables === 'undefined' ||
      typeof cohorts === 'undefined'
    ) {
      commit(mutations.SET_PAIRWISE_TUKEY_HSD_PVALS, []);
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
        groups.push({ id: c.id, label: c.label, data: cohortData });
      }
    });
    const numGroups = groups.length;

    // need at least 3 groups for statsmodel Tukey HSD
    if (numGroups < 3) return;

    // pass _all_ observation variables, not just the selected ones
    const outputVariables = [];
    collection.observation_variables.forEach(v => {
      v.children.forEach(c => {
        outputVariables.push(c);
      });
    });

    try {
      const { data } = await axios.post(`/api/compute-pairwise-tukeyhsd`, {
        numGroups,
        groups,
        outputVariables,
      });
      commit(mutations.SET_PAIRWISE_TUKEY_HSD_PVALS, data.results);
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    }
  },
};
