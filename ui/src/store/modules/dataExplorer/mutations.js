import { mutations, state as stateTypes } from './types';

export default {
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
};
