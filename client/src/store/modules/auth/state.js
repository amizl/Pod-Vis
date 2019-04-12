import { state } from './types';

export default {
  [state.USER]: {
    id: 0,
    email: '',
    name: '',
    institution: '',
  },
  /**
   * If there is an authentication error, i.e., incorrect password
   * or email, then this state will trigger the red box inside of the
   *
   */
  [state.AUTH_ERROR]: null,
  [state.IS_LOADING]: false,
};
