import Vue from 'vue';
import Vuex from 'vuex';
import * as firebase from 'firebase';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: null,
    loading: false,
    authError: null,
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
          // For development, will handle this later.
          /* eslint-disable-next-line no-console */
          console.log(error);
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
        })
        .catch((error) => {
          commit('setLoading', false);
          commit('setAuthError', error.message);
          // For development, will handle this later.
          /* eslint-disable-next-line no-console */
          // console.log(error);
        });
    },
    signUserOut({ commit }) {
      // commit('settingLoading', true);
      firebase
        .auth()
        .signOut()
        .then(() => {
          // commit('settingLoading', false);
          commit('setUser', null);
        });
    },
    autoSignIn({ commit }, payload) {
      commit('setUser', payload.uid);
    },
  },
});
