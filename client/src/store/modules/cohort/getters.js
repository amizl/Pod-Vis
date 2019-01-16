import { getters, state as stateTypes } from './types';

export default {
  [getters.GET_DATASET_NAME](state) {
    // todo: dataset should be renamed to name in schema
    return state[stateTypes.DATASET].dataset;
  },
};
