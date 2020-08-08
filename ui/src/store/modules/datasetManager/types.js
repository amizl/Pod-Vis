export const state = {
  DATASETS: 'datasets',
  COLLECTION: 'collection',
  COLLECTIONS: 'collections',
  IS_LOADING: 'isLoading',
  SELECTED_DATASETS: 'selectedDatasets',
};

export const getters = {};

export const mutations = {
  SET_DATASETS: 'setDatasets',
  SET_COLLECTION: 'setCollection',
  SET_COLLECTIONS: 'setCollections',
  ADD_COLLECTION: 'addCollection',
  SET_LOADING: 'setLoading',
  SET_SELECTED_DATASETS: 'setSelectedDatasets',
  CLEAR_SELECTED_DATASETS: 'clearSelectedDatasets',
  DELETE_COLLECTION: 'deleteCollection',
};

export const actions = {
  FETCH_DATASETS: 'fetchDatasets',
  FETCH_COLLECTION: 'fetchCollection',
  FETCH_COLLECTIONS: 'fetchCollections',
  SELECT_DATASETS: 'selectDatasets',
  ADD_SELECTED_DATASETS_TO_COHORTS: 'addToCohorts',
  SAVE_COLLECTION: 'saveCollection',
  DELETE_COLLECTION: 'deleteCollection',
};
