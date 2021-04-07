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
   * @param {*} newFirstVisits
   */
  [mutations.SET_FIRST_VISITS](state, newFirstVisits) {
    state[stateTypes.FIRST_VISITS] = newFirstVisits;
  },
  /**
   * Set last visit variables.
   * @param {*} state
   * @param {*} newLastVisit
   */
  [mutations.SET_LAST_VISITS](state, newLastVisits) {
    state[stateTypes.LAST_VISITS] = newLastVisits;
  },
  /**
   * Set visit variable.
   * @param {*} state
   * @param {*} newVisitVar
   */
  [mutations.SET_VISIT_VARIABLE](state, newVisitVar) {
    state[stateTypes.VISIT_VARIABLE] = newVisitVar;
  },
  /**
   * Set times between visits.
   * @param {*} state
   * @param {*} newTimesVar
   */
  [mutations.SET_TIMES_BETWEEN_VISITS](state, newTimesVar) {
    state[stateTypes.TIMES_BETWEEN_VISITS] = newTimesVar;
  },
  /**
   * Set number of selected subjects.
   * @param {*} state
   * @param {*} newSelectedSubjectsVar
   */
  [mutations.SET_NUM_SELECTED_SUBJECTS](state, newSelectedSubjectsVar) {
    state[stateTypes.NUM_SELECTED_SUBJECTS] = newSelectedSubjectsVar;
  },
};
