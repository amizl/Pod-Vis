export const state = {
  DATASETS: 'datasets',
  COLLECTIONS: 'collections',
  IS_LOADING: 'isLoading',
  SELECTED_DATASETS: 'selectedDatasets',
};

export const getters = {};

export const mutations = {
  SET_DATASETS: 'setDatasets',
  SET_COLLECTIONS: 'setCollections',
  ADD_COLLECTION: 'addCollection',
  SET_LOADING: 'setLoading',
  SET_SELECTED_DATASETS: 'setSelectedDatasets',
};

export const actions = {
  FETCH_DATASETS: 'fetchDatasets',
  FETCH_COLLECTIONS: 'fetchCollections',
  SELECT_DATASETS: 'selectDatasets',
  ADD_SELECTED_DATASETS_TO_COHORTS: 'addToCohorts',
  SAVE_COLLECTION: 'saveCollection',
};
