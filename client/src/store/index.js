import Vue from 'vue';
import Vuex from 'vuex';
import * as firebase from 'firebase';
import modules from './modules';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    browserDatasets: null,
  },
  modules,
  mutations: {
    setBrowserDatasets(state, payload) {
      state.browserDatasets = payload;
    },
  },
  actions: {
    fetchBrowserDatasets({ commit }) {
      commit('setLoading', true);

      firebase
        .firestore()
        .collection('datasets')
        .get()
        .then((querySnapshot) => {
          const datasets = querySnapshot
            .docs
            .map(doc => doc.data());

          commit('setBrowserDatasets', datasets);
          commit('setLoading', false);
        })
        /* eslint-disable-next-line */
        .catch((error) => {
          // TODO
        });
    },
  },
});
