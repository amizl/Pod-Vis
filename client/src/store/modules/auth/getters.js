import { GETTERS } from './types';

export default {
  [GETTERS.USER]: state => state.user,
  [GETTERS.AUTH_ERROR]: state => state.authError,
  [GETTERS.LOADING]: state => state.loading,
};
