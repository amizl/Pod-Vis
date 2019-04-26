import { getters, state as stateTypes } from './types';

export default {
  /**
   * Checks if the user is authenticated
   *
   * The user is not authenticated if the server does not
   * validate their token when first hitting the SPA. If
   * token is not validated, the user object is not set
   * and will remain with its falsy values set in state.js
   */
  [getters.IS_USER_AUTHENTICATED]: state =>
    Boolean(
      state[stateTypes.USER] &&
        state[stateTypes.USER].id &&
        state[stateTypes.USER].email &&
        state[stateTypes.USER].name
    ),
};
