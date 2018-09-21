import * as firebase from 'firebase';
import { actions, mutations } from './types';

export default {
  [actions.CREATE_USER_ACCOUNT]({ commit }, payload) {
    commit(mutations.MUTATE_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    firebase
      .auth()
      .createUserWithEmailAndPassword(payload.email, payload.password)
      .then(({ user }) => {
        commit(mutations.MUTATE_LOADING, false);
        commit(mutations.MUTATE_USER, {
          id: user.uid,
        });
      })
      .catch((error) => {
        commit('setLoading', false);
        commit('setAuthError', error.message);
      });
  },
  [actions.SIGN_USER_IN]({ commit }, payload) {
    commit(mutations.MUTATE_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    firebase
      .auth()
      .signInWithEmailAndPassword(payload.email, payload.password)
      .then(({ user }) => {
        commit(mutations.MUTATE_USER, {
          id: user.uid,
          username: user.email,
        });
        commit(mutations.MUTATE_LOADING, false);
        // user
        //   .getIdToken(/* forceRefresh */ true)
        //   .then((idToken) => {
        //     console.log(idToken);
        //   });
      })
      .catch((error) => {
        commit(mutations.MUTATE_LOADING, false);
        commit(mutations.MUTATE_AUTH_ERROR, error.message);
      });
  },
  [actions.SIGN_USER_OUT]({ commit }) {
    commit(mutations.MUTATE_LOADING, true);
    firebase
      .auth()
      .signOut()
      .then(() => {
        commit(mutations.CLEAR_USER);
        commit(mutations.MUTATE_LOADING, false);
      });
  },
  [actions.AUTO_SIGN_IN]({ commit }, payload) {
    commit(mutations.MUTATE_USER, payload.uid);
  },
};
