import * as firebase from 'firebase';
import { actions, mutations } from './types';

export default {
  [actions.CREATE_USER_ACCOUNT]({ commit }, payload) {
    commit(mutations.SET_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    firebase
      .auth()
      .createUserWithEmailAndPassword(payload.email, payload.password)
      .then(({ user }) => {
        commit(mutations.SET_LOADING, false);
        commit(mutations.SET_USER, {
          id: user.uid,
        });
      })
      .catch((error) => {
        commit(mutations.SET_USER, false);
        commit(mutations.SET_AUTH_ERROR, error.message);
      });
  },
  [actions.SIGN_USER_IN]({ commit }, payload) {
    commit(mutations.SET_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    firebase
      .auth()
      .signInWithEmailAndPassword(payload.email, payload.password)
      .then(({ user }) => {
        commit(mutations.SET_USER, {
          id: user.uid,
          username: user.email,
        });
        commit(mutations.SET_LOADING, false);
        // user
        //   .getIdToken(/* forceRefresh */ true)
        //   .then((idToken) => {
        //     console.log(idToken);
        //   });
      })
      .catch((error) => {
        commit(mutations.SET_LOADING, false);
        commit(mutations.SET_AUTH_ERROR, error.message);
      });
  },
  [actions.SIGN_USER_OUT]({ commit }) {
    commit(mutations.SET_LOADING, true);
    firebase
      .auth()
      .signOut()
      .then(() => {
        commit(mutations.CLEAR_USER);
        commit(mutations.SET_LOADING, false);
      });
  },
  [actions.AUTO_SIGN_IN]({ commit }, payload) {
    commit(mutations.SET_USER, payload.uid);
  },
};
