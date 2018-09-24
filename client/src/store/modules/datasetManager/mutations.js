import { mutations } from './types';

export default {
  [mutations.SET_DATASETS](state, payload) {
    state.datasets = payload;
  },
  [mutations.SET_LOADING](state, payload) {
    state.loading = payload;
  },
  [mutations.SET_SELECTED_DATASETS](state, payload) {
    if (payload.length) {
      state.selected_datasets = payload;
    } else {
      state.selected_datasets = null;
    }
  },
};
