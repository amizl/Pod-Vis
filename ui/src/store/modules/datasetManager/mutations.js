import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_DATASETS](state, datasets) {
    state[stateTypes.DATASETS] = datasets;
  },
  [mutations.SET_COLLECTIONS](state, collections) {
    state[stateTypes.COLLECTIONS] = collections;
  },
  [mutations.SET_COLLECTION](state, collection) {
    state[stateTypes.COLLECTION] = collection;
  },
  [mutations.ADD_COLLECTION](state, collection) {
    state[stateTypes.COLLECTIONS].push(collection);
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
  [mutations.CLEAR_SELECTED_DATASETS](state) {
    state[stateTypes.SELECTED_DATASETS] = [];
  },
  [mutations.DELETE_COLLECTION](state, collectionId) {
    const collections = state[stateTypes.COLLECTIONS];
    state[stateTypes.COLLECTIONS] = collections.filter(
      collection => collection.id !== collectionId
    );
  },
};
