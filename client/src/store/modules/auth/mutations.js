import { mutations } from './types';

export default {
  [mutations.MUTATE_USER](state, payload) {
    state.user = payload;
  },
  [mutations.CLEAR_USER](state) {
    state.user = null;
  },
  [mutations.MUTATE_LOADING](state, payload) {
    state.loading = payload;
  },
  [mutations.MUTATE_AUTH_ERROR](state, payload) {
    state.authError = payload;
  },
  [mutations.CLEAR_AUTH_ERROR](state) {
    state.authError = null;
  },
};
