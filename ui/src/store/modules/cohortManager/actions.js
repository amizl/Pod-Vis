import axios from 'axios';
import { actions, mutations } from './types';

export default {
  async [actions.FETCH_COHORTS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/cohorts');
      commit(mutations.SET_COHORTS, data.cohorts);
    } catch (err) {
      // TODO
    }

    commit(mutations.SET_LOADING, false);
  },
};
