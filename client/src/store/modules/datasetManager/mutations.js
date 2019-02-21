import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_DATASETS](state, payload) {
    state[stateTypes.DATASETS] = payload;
  },
  [mutations.SET_LOADING](state, payload) {
    state[stateTypes.IS_LOADING] = payload;
  },
  [mutations.SET_SELECTED_DATASETS](state, payload) {
    // May need to consider using Vue.set in the case
    // child componenets are not updating
    if (payload.length) {
      state[stateTypes.SELECTED_DATASETS] = payload;
    } else {
      state[stateTypes.SELECTED_DATASETS] = [];
    }
  },
};
