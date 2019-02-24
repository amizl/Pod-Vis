import { actions, mutations } from './types';

export default {
  /**
   *  Notify
   * @param {function} commit
   * @param {object} notification Notifcation obect with a type and message
   * key. Type can be 'success' or 'error' to determine the kind of toast.
   */
  [actions.NOTIFY]({ commit }, notification = null) {
    commit(mutations.SET_NOTIFICATION, notification);
    commit(mutations.SET_NOTIFY, notification !== null ? true : false);
  },
};
