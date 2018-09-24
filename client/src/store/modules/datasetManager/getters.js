import { getters } from './types';

export default {
  [getters.DATASETS]: state => state.datasets,
  [getters.LOADING]: state => state.loading,
  [getters.SELECTED_DATASETS]: state => state.selected_datasets,
};
