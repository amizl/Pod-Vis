import axios from 'axios';
import { actions, mutations } from './types';

export default {
  /**
   *  Create user account.
   * @param {Object} commit
   * @param {Object} payload Email and password.
   */
  async [actions.CREATE_USER_ACCOUNT]({ commit }, { email, password }) {
    commit(mutations.SET_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    try {
      const { data } = await axios.post('/auth/signup', {
        email,
        password,
      });
      commit(mutations.SET_USER, {
        ...data.user,
      });
    } catch (err) {
      const { error } = err.response.data;
      commit(mutations.SET_AUTH_ERROR, error);
    }
  },
  /**
   *  Sign the user in.
   * @param {*} commit
   * @param {*} payload Email and password
   */
  async [actions.SIGN_USER_IN]({ commit }, { email, password }) {
    commit(mutations.SET_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    try {
      const { data } = await axios.post('/auth/signin', {
        email,
        password,
      });
      commit(mutations.SET_USER, {
        ...data.user,
      });
    } catch (err) {
      const { error } = err.response.data;
      commit(mutations.SET_AUTH_ERROR, error);
    }

    commit(mutations.SET_LOADING, false);
  },
  async [actions.SIGN_USER_OUT]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      await axios.delete('/auth/signout');
      commit(mutations.CLEAR_USER);
      commit(mutations.SET_LOADING, false);
    } catch (err) {
      console.log('uh');
    }
  },
  [actions.AUTO_SIGN_IN]({ commit }, payload) {
    commit(mutations.SET_USER, payload.uid);
  },
};
