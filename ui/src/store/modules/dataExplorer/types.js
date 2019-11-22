// State
export const state = {
  COLLECTION: 'collection',
  COHORTS: 'cohorts',
  VISIBLE_COHORTS: 'visibleCohorts',
  IS_LOADING: 'isLoading',
  OUTCOME_VARIABLES: 'outcomeVariables',
  DATA: 'data',
  RAW_DATA: 'rawData',
  DETAILED_VIEW: 'detailedView',
  ANOVA_PVALS: 'anovaPvals',
};

// Getters
export const getters = {};

// Mutations
export const mutations = {
  SET_COHORTS: 'setCohorts',
  SET_VISIBLE_COHORTS: 'setVisibleCohorts',
  SET_LOADING: 'setLoading',
  SET_COLLECTION: 'setCollection',
  SET_OUTCOME_VARIABLES: 'setOutcomeVariables',
  SET_DATA: 'setData',
  SET_RAW_DATA: 'setRawData',
  SET_DETAILED_VIEW: 'setDetailedView',
  SET_ANOVA_PVALS: 'setAnovaPvals',
};

// Actions
export const actions = {
  FETCH_COLLECTION: 'fetchCollection',
  FETCH_COHORTS: 'fetchCohort',
  ANALYZE_COHORTS: 'analyzeCohorts',
  SET_VISIBLE_COHORTS: 'setVisibleCohorts',
  SET_OUTCOME_VARIABLES: 'setOutcomeVariables',
  FETCH_DATA: 'fetchData',
  FETCH_RAW_DATA: 'fetchRawData',
  SET_DETAILED_VIEW: 'setDetailedView',
  SET_COHORT_SUBJECTS: 'setCohortSubjects',
};
