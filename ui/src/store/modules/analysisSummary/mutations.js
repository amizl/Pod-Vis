import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_SELECTED_COHORTS](state, cohorts) {
    state[stateTypes.SELECTED_COHORTS] = cohorts;
  },

  [mutations.SET_SELECTED_OUTCOME_VARIABLE](state, outcomeVariable) {
    state[stateTypes.SELECTED_OUTCOME_VARIABLE] = outcomeVariable;
  },

  [mutations.SET_PAIRWISE_TUKEY_HSD_PVALS](state, pvals) {
    state[stateTypes.PAIRWISE_TUKEY_HSD_PVALS] = pvals;
  },
};
