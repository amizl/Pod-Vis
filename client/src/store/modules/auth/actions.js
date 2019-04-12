import router from '@/router';
import {
  SuccessNotification,
  ErrorNotification,
} from '@/store/modules/notifications/notifications';
import axios from 'axios';
import { actions, mutations } from './types';

export default {
  /**
   *  Create user account.
   * @param {Object} commit
   * @param {Object} payload Email, password, name, and institution.
   *
   *  Returns promises to allow caller add logic based on action.
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
      commit(mutations.SET_LOADING, false);
      return new Promise(resolve => resolve());
    } catch (err) {
      const { error } = err.response.data;
      commit(mutations.SET_AUTH_ERROR, error);
      commit(mutations.SET_LOADING, false);
      return new Promise((resolve, reject) => reject());
    }
  },
  /**
   *  Sign the user in.
   * @param {*} commit
   * @param {*} payload Email and password
   * Returns promises to allow caller add logic based on action.
   */
  async [actions.SIGN_USER_IN]({ commit }, { email, password }) {
    commit(mutations.SET_LOADING, true);
    commit(mutations.CLEAR_AUTH_ERROR);

    try {
      const { data } = await axios.post('/auth/signin', {
        email,
        password,
      });
      commit(mutations.SET_USER, data.user);
      commit(mutations.SET_LOADING, false);

      return new Promise(resolve => resolve());
    } catch (err) {
      const { error } = err.response.data;
      commit(mutations.SET_AUTH_ERROR, error);
      commit(mutations.SET_LOADING, false);

      return new Promise((resolve, reject) => reject());
    }
  },
  /**
   * Sign the user out.
   * @param {Object} commit
   */
  async [actions.SIGN_USER_OUT]({ commit, dispatch }) {
    commit(mutations.SET_LOADING, true);

    try {
      await axios.delete('/auth/signout');
      commit(mutations.CLEAR_USER);
      router.push('/signin');
      const notification = new SuccessNotification(
        'You have successfully logged out.'
      );
      dispatch(notification.dispatch, notification, {
        root: true,
      });
    } catch (err) {
      // what should we do when this errors?
    }
    commit(mutations.SET_LOADING, false);
  },
  /**
   * Set user if there is an active session.
   * @param {Object} commit
   */
  async [actions.GET_USER_FROM_SESSION]({ commit, dispatch }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/auth/signin');
      commit(mutations.SET_USER, data.user);
      commit(mutations.SET_LOADING, false);

      return new Promise(resolve => resolve());
    } catch (err) {
      const { data } = err.response;
      // TODO:
      // Need a nicer way to check for what happened on server
      // (is there no cookie or has that cookie w/ token expired?)
      if (data.msg.includes('expired')) {
        const error = new ErrorNotification('Your session has expired.');
        dispatch(error.dispatch, error, { root: true });
      }
      commit(mutations.SET_LOADING, false);

      return new Promise((resolve, reject) => reject());
    }
  },
};
