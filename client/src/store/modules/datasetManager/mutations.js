import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_DATASETS](state, datasets) {
    state[stateTypes.DATASETS] = datasets;
  },
  [mutations.SET_LOADING](state, loading) {
    state[stateTypes.IS_LOADING] = loading;
  },
  [mutations.SET_SELECTED_DATASETS](state, selectedDatasets) {
    // May need to consider using Vue.set in the case
    // child componenets are not updating
    if (selectedDatasets.length) {
      state[stateTypes.SELECTED_DATASETS] = selectedDatasets;
    } else {
      state[stateTypes.SELECTED_DATASETS] = [];
    }
  },
};
