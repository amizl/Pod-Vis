// State
export const state = {
  COHORTS: 'cohorts',
  IS_LOADING: 'isLoading',
  COLLECTION: 'collection',
  UNFILTERED_DATA: 'unfilteredData',
  FILTERED_DATA: 'filteredData',
  INPUT_VARIABLES: 'inputVariables',
  OUTPUT_VARIABLES: 'outputVariables',
  CROSS_FILTER: 'crossFilter',
  DIMENSIONS: 'dimensions',
};

// Getters
export const getters = {};

// Mutations
export const mutations = {
  SET_COHORTS: 'setCohorts',
  SET_COLLECTION: 'setCollection',
  SET_LOADING: 'setLoading',
  SET_DATA: 'setData',
  ADD_INPUT_VARIABLE: 'addInputVariable',
  REMOVE_INPUT_VARIABLE: 'removeInputVariable',
  SET_INPUT_VARIABLES: 'setInputVariables',
  REMOVE_OUTPUT_VARIABLE: 'removeOutputVariable',
  SET_OUTPUT_VARIABLES: 'setOutputVariables',
  INITIALIZE_CROSS_FILTER: 'initializeCrossFilter',
  UPDATE_FILTERED_DATA: 'updateDataFromFilters',
  ADD_DIMENSION: 'addDimension',
  REMOVE_DIMENSION: 'removeDimension',
  ADD_FILTER: 'addFilter',
  CLEAR_FILTER: 'clearFilter',
};

// Actions
export const actions = {
  FETCH_COHORTS: 'fetchCohorts',
  FETCH_COLLECTION: 'fetchCollection',
  FETCH_DATA: 'fetchData',
  ADD_INPUT_VARIABLE: 'addInputVariable',
  REMOVE_INPUT_VARIABLE: 'removeInputVariable',
  SET_INPUT_VARIABLES: 'setInputVariables',
  REMOVE_OUTPUT_VARIABLE: 'removeOutputVariable',
  SET_OUTPUT_VARIABLES: 'setOutputVariables',
  ADD_OUTPUT_VARIABLE: 'addOutputVariable',
  ADD_DIMENSION: 'addDimension',
  ADD_FILTER: 'addFilter',
  CLEAR_FILTER: 'clearFilter',
};
