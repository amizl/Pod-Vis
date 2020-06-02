import Vue from 'vue';
import * as crossfilter from 'crossfilter2';
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
  [mutations.SET_COLLECTION_SUMMARY](state, collection_summary) {
    state[stateTypes.COLLECTION_SUMMARY] = collection_summary;
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
};
