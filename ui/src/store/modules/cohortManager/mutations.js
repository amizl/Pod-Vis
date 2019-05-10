import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_COHORTS](state, cohorts) {
    state[stateTypes.COHORTS] = cohorts;
  },
  [mutations.SET_LOADING](state, isLoading) {
    state[stateTypes.IS_LOADING] = isLoading;
  },
  [mutations.SET_COLLECTION](state, collection) {
    state[stateTypes.COLLECTION] = collection;
  },
};
