import { mutations, state as stateTypes } from './types';

export default {
  /**
   *
   * @param {Object} state Global data explorer state.
   * @param {Object} outcomeVariable Outcome variable selected in analysis summary.
   */
  [mutations.SET_SELECTED_OUTCOME_VARIABLE](state, outcomeVariable) {
    state[stateTypes.SELECTED_OUTCOME_VARIABLE] = outcomeVariable;
  },

  [mutations.SET_PAIRWISE_TUKEY_HSD_PVALS](state, pvals) {
    state[stateTypes.PAIRWISE_TUKEY_HSD_PVALS] = pvals;
  },
};
