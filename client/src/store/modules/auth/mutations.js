import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_USER](state, payload) {
    state[stateTypes.USER] = payload;
  },
  [mutations.CLEAR_USER](state) {
    state[stateTypes.USER] = {
      id: 0,
      email: '',
      name: '',
      institution: '',
    };
  },
  [mutations.SET_LOADING](state, payload) {
    state[stateTypes.IS_LOADING] = payload;
  },
  [mutations.SET_AUTH_ERROR](state, payload) {
    state[stateTypes.AUTH_ERROR] = payload;
  },
  [mutations.CLEAR_AUTH_ERROR](state) {
    state[stateTypes.AUTH_ERROR] = null;
  },
};
