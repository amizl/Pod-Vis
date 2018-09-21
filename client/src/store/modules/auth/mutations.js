import { MUTATIONS } from './types';

export default {
  [MUTATIONS.MUTATE_USER](state, payload) {
    state.user = payload;
  },
  [MUTATIONS.CLEAR_USER](state) {
    state.user = null;
  },
  [MUTATIONS.MUTATE_LOADING](state, payload) {
    state.loading = payload;
  },
  [MUTATIONS.MUTATE_AUTH_ERROR](state, payload) {
    state.authError = payload;
  },
  [MUTATIONS.CLEAR_AUTH_ERROR](state) {
    state.authError = null;
  },
};
