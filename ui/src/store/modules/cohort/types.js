// State
export const state = {
  DATASET: 'dataset',
  IS_LOADING: 'isLoading',
  COHORT_SELECTION: 'cohortSelection',
};

// Getters
export const getters = {
  GET_DATASET_NAME: 'getDatasetName',
};

// Mutations
export const mutations = {
  SET_DATASET: 'setDataset',
  SET_LOADING: 'setLoading',
  SET_COHORT_SELECTION: 'setCohortSelection',
};

// Actions
export const actions = {
  FETCH_DATASET: 'fetchDataset',
  SET_COHORT_SELECTION: 'setCohortSelection',
};
