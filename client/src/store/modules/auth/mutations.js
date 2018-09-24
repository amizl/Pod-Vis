import { mutations } from './types';

export default {
  [mutations.SET_USER](state, payload) {
    state.user = payload;
  },
  [mutations.CLEAR_USER](state) {
    state.user = null;
  },
  [mutations.SET_LOADING](state, payload) {
    state.loading = payload;
  },
  [mutations.SET_AUTH_ERROR](state, payload) {
    state.authError = payload;
  },
  [mutations.CLEAR_AUTH_ERROR](state) {
    state.authError = null;
  },
};
