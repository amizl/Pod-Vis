import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_LOADING](state, payload) {
    state[stateTypes.IS_LOADING] = payload;
  },
  [mutations.SET_DATASETS](state, payload) {
    state[stateTypes.DATASETS].push(...payload);
  },
};
