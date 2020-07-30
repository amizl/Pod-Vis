// State
export const state = {
  SELECTED_COHORTS: 'selectedCohorts',
  SELECTED_OUTCOME_VARIABLE: 'selectedOutcomeVariable',
  PAIRWISE_TUKEY_HSD_PVALS: 'pairwiseTukeyHsdPvals',
};

// Getters
export const getters = {};

// Mutations
export const mutations = {
  SET_SELECTED_COHORTS: 'setSelectedCohorts',
  SET_SELECTED_OUTCOME_VARIABLE: 'setSelectedOutcomeVariable',
  SET_PAIRWISE_TUKEY_HSD_PVALS: 'setPairwiseTukeyHsdPvals',
};

// Actions
export const actions = {
  SET_SELECTED_COHORTS: 'setSelectedCohorts',
  SET_SELECTED_OUTCOME_VARIABLE: 'setSelectedOutcomeVariable',
  ANALYZE_COHORTS: 'analyzeCohorts',
};
