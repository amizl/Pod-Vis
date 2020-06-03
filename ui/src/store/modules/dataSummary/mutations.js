import Vue from 'vue';
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
  [mutations.SET_COLLECTION_SUMMARIES](state, collection_summaries) {
    state[stateTypes.COLLECTION_SUMMARIES] = collection_summaries;
  },
  /**
   * Set first visit variables.
   * @param {*} state
   * @param {*} newFirstVisit
   */
  [mutations.SET_FIRST_VISIT](state, newFirstVisit) {
    state[stateTypes.FIRST_VISIT] = newFirstVisit;
  },
  /**
   * Set last visit variables.
   * @param {*} state
   * @param {*} newLastVisit
   */
  [mutations.SET_LAST_VISIT](state, newLastVisit) {
    state[stateTypes.LAST_VISIT] = newLastVisit;
  },
  /**
   * Set visit variable.
   * @param {*} state
   * @param {*} newVisitVar
   */
  [mutations.SET_VISIT_VARIABLE](state, newVisitVar) {
    state[stateTypes.VISIT_VARIABLE] = newVisitVar;
  },
};
