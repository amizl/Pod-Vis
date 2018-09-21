import getters from './getters';
import actions from './actions';
import mutations from './mutations';

export default {
  namespaced: true,
  state: {
    user: null,
    loading: false,
    authError: null,
  },
  getters,
  mutations,
  actions,
};
