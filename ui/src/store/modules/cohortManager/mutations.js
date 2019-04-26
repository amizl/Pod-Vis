import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_COHORTS](state, payload) {
    state[stateTypes.COHORTS] = payload;
  },
  [mutations.SET_LOADING](state, payload) {
    state[stateTypes.IS_LOADING] = payload;
  },
};
