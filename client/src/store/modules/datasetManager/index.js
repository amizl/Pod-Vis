import getters from './getters';
import mutations from './mutations';
import actions from './actions';

export default {
  namespaced: true,
  state: {
    datasets: null,
    selected_datasets: null,
    loading: false,
  },
  getters,
  mutations,
  actions,
};
