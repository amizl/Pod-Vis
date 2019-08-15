import { mutations, state as stateTypes } from './types';

export default {
  /**
   * Set cohorts mutation.
   * @param {*} state
   * @param {*} cohorts
   */
  [mutations.SET_COHORTS](state, cohorts) {
    state[stateTypes.COHORTS] = cohorts;
  },
  /**
   * Set loading mutation.
   * @param {Object} state
   * @param {Boolean} isLoading Flag whether or not we are waiting on data.
   */
  [mutations.SET_LOADING](state, isLoading) {
    state[stateTypes.IS_LOADING] = isLoading;
  },
  /**
   * Set collection mutation.
   * @param {Object} state Global cohort manager state.
   * @param {Object} collection
   */
  [mutations.SET_COLLECTION](state, collection) {
    state[stateTypes.COLLECTION] = collection;
  },
  /**
   *
   * @param {Object} state Global data explorer state.
   * @param {Array[Object]} outcomeVariables Outcome variables selected in data explorer.
   */
  [mutations.SET_OUTCOME_VARIABLES](state, outcomeVariables) {
    state[stateTypes.OUTCOME_VARIABLES] = outcomeVariables;
  },
  [mutations.SET_DATA](state, data) {
    state[stateTypes.DATA] = data;
  },
  [mutations.SET_DETAILED_VIEW](state, detailedView) {
    state[stateTypes.DETAILED_VIEW] = detailedView;
  },
};
