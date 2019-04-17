export const state = {
  DATASETS: 'datasets',
  IS_LOADING: 'isLoading',
  SELECTED_DATASETS: 'selectedDatasets',
};

export const getters = {};

export const mutations = {
  SET_DATASETS: 'setDatasets',
  SET_LOADING: 'setLoading',
  SET_SELECTED_DATASETS: 'setSelectedDatasets',
};

export const actions = {
  FETCH_DATASETS: 'fetchDatasets',
  SELECT_DATASETS: 'selectDatasets',
  ADD_SELECTED_DATASETS_TO_COHORTS: 'addToCohorts',
  SAVE_COLLECTION: 'saveCollection',
};
