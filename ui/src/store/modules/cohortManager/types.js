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
  PVALS: 'pvals',
  QUERIES: 'queries',
};

// Getters
export const getters = {
  HAS_USER_FILTERED_INPUT_VARIABLES: 'hasUserFilteredInputVariables',
};

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
  SET_PVALS: 'setPvals',
  SET_QUERY: 'setQuery',
  CLEAR_QUERY: 'clearQuery',
  RESET_COHORTS: 'resetCohorts',
  RESET_IS_LOADING: 'resetIsLoading',
  RESET_COLLECTION: 'resetCollection',
  RESET_UNFILTERED_DATA: 'resetUnfilteredData',
  RESET_FILTERED_DATA: 'resetFilteredData',
  RESET_INPUT_VARIABLES: 'resetInputVariables',
  RESET_OUTPUT_VARIABLES: 'resetOutputVariables',
  RESET_CROSS_FILTER: 'resetCrossfilter',
  RESET_DIMENSIONS: 'resetDimensions',
  RESET_PVALS: 'resetPvals',
  RESET_QUERIES: 'resetQueries',
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
  ANALYZE_FILTERED: 'analyzeFilterd',
  ADD_QUERY: 'addQuery',
  RESET_ALL_STORE_DATA: 'resetAllStoreData',
  SAVE_COHORT: 'saveCohort',
};
