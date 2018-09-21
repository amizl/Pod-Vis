import * as firebase from 'firebase';
import { ACTIONS, MUTATIONS } from './types';

export default {
  [ACTIONS.CREATE_USER]({ commit }, payload) {
    commit(MUTATIONS.MUTATE_LOADING, true);
    commit(MUTATIONS.CLEAR_AUTH_ERROR);

    firebase
      .auth()
      .createUserWithEmailAndPassword(payload.email, payload.password)
      .then(({ user }) => {
        commit(MUTATIONS.MUTATE_LOADING, false);
        commit(MUTATIONS.MUTATE_USER, {
          id: user.uid,
        });
      })
      .catch((error) => {
        commit('setLoading', false);
        commit('setAuthError', error.message);
      });
  },
  [ACTIONS.SIGN_USER_IN]({ commit }, payload) {
    commit(MUTATIONS.MUTATE_LOADING, true);
    commit(MUTATIONS.CLEAR_AUTH_ERROR);

    firebase
      .auth()
      .signInWithEmailAndPassword(payload.email, payload.password)
      .then(({ user }) => {
        commit(MUTATIONS.MUTATE_USER, {
          id: user.uid,
          username: user.email,
        });
        commit(MUTATIONS.MUTATE_LOADING, false);
        // user
        //   .getIdToken(/* forceRefresh */ true)
        //   .then((idToken) => {
        //     console.log(idToken);
        //   });
      })
      .catch((error) => {
        commit(MUTATIONS.MUTATE_LOADING, false);
        commit(MUTATIONS.MUTATE_AUTH_ERROR, error.message);
      });
  },
  [ACTIONS.SIGN_USER_OUT]({ commit }) {
    commit(MUTATIONS.MUTATE_LOADING, true);
    firebase
      .auth()
      .signOut()
      .then(() => {
        commit(MUTATIONS.CLEAR_USER);
        commit(MUTATIONS.MUTATE_LOADING, false);
      });
  },
  [ACTIONS.AUTO_SIGN_IN]({ commit }, payload) {
    commit(MUTATIONS.MUTATE_USER, payload.uid);
  },
};
