import Vue from 'vue';
import Vuex from 'vuex';
import * as firebase from 'firebase';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: null,
    loading: false,
    authError: null,
    browserDatasets: null,
  },
  getters: {
    user(state) {
      return state.user;
    },
    authError(state) {
      return state.authError;
    },
    loading(state) {
      return state.loading;
    },
    browserDatasets(state) {
      return state.browserDatasets;
    },
  },
  mutations: {
    setUser(state, payload) {
      state.user = payload;
    },
    setLoading(state, payload) {
      state.loading = payload;
    },
    setAuthError(state, payload) {
      state.authError = payload;
    },
    clearAuthError(state) {
      state.authError = null;
    },
    setBrowserDatasets(state, payload) {
      state.browserDatasets = payload;
    },
  },
  actions: {
    createUserAccount({ commit }, payload) {
      commit('setLoading', true);
      commit('clearAuthError');

      firebase
        .auth()
        .createUserWithEmailAndPassword(payload.email, payload.password)
        .then(({ user }) => {
          commit('setLoading', false);
          commit('setUser', {
            id: user.uid,
          });
        })
        .catch((error) => {
          commit('setLoading', false);
          commit('setAuthError', error.message);
        });
    },
    signUserIn({ commit }, payload) {
      commit('setLoading', true);
      commit('clearAuthError');

      firebase
        .auth()
        .signInWithEmailAndPassword(payload.email, payload.password)
        .then(({ user }) => {
          commit('setLoading', false);
          commit('setUser', {
            id: user.uid,
            username: user.email,
          });
          // user
          //   .getIdToken(/* forceRefresh */ true)
          //   .then((idToken) => {
          //     console.log(idToken);
          //   });
        })
        .catch((error) => {
          commit('setLoading', false);
          commit('setAuthError', error.message);
        });
    },
    signUserOut({ commit }) {
      commit('setLoading', true);
      firebase
        .auth()
        .signOut()
        .then(() => {
          commit('setUser', null);
          commit('setLoading', false);
        });
    },
    autoSignIn({ commit }, payload) {
      commit('setUser', payload.uid);
    },
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
