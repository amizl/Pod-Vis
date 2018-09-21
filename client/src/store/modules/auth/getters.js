import { getters } from './types';

export default {
  [getters.USER]: state => state.user,
  [getters.AUTH_ERROR]: state => state.authError,
  [getters.LOADING]: state => state.loading,
};
