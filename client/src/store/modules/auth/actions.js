import router from '@/router';
import axios from 'axios';
import { actions, mutations } from './types';

export default {
  /**
   *  Create user account.
   * @param {Object} commit
   * @param {Object} payload Email, password, name, and institution.
   */
  async [actions.CREATE_USER_ACCOUNT]({ commit }, payload) {
    commit(mutations.SET_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    const { email, password, name, institution } = payload;
    try {
      const { data } = await axios.post('/auth/signup', {
        email,
        password,
        name,
        institution,
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
  /**
   * Sign the user out.
   * @param {Object} commit
   */
  async [actions.SIGN_USER_OUT]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      await axios.delete('/auth/signout');
      commit(mutations.CLEAR_USER);
      router.push('/signin');
    } catch (err) {
      // what should we do when this errors?
    }
    commit(mutations.SET_LOADING, false);
  },
  /**
   * Set user if there is an active session.
   * @param {Object} commit
   */
  async [actions.GET_USER_FROM_SESSION]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/auth/signin');
      commit(mutations.SET_USER, {
        ...data.user,
      });
    } catch (err) {
      // No active session
    }

    commit(mutations.SET_LOADING, false);
  },
};
