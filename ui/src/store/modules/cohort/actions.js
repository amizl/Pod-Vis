// import store from '@/store';
import { actions, mutations } from './types';

export default {
  async [actions.FETCH_DATASET]({ commit }, payload) {
    // commit(mutations.SET_LOADING, true);
  },
  [actions.SET_COHORT_SELECTION]({ commit }, payload) {
    // commit(mutations.SET_COHORT_SELECTION, payload);
  },
};
