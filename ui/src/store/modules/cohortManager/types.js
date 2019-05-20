// State
export const state = {
  COHORTS: 'cohorts',
  IS_LOADING: 'isLoading',
  COLLECTION: 'collection',
  DATA: 'data',
  INPUT_VARIABLES: 'inputVariables',
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
};

// Actions
export const actions = {
  FETCH_COHORTS: 'fetchCohorts',
  FETCH_COLLECTION: 'fetchCollection',
  FETCH_DATA: 'fetchData',
  ADD_INPUT_VARIABLE: 'addInputVariable',
  REMOVE_INPUT_VARIABLE: 'removeInputVariable',
  SET_INPUT_VARIABLES: 'setInputVariables',
};
