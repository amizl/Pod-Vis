import { state } from './types';

export default {
  [state.COHORTS]: [],
  [state.COHORT]: { id: null },
  [state.IS_LOADING]: false,
  [state.COLLECTION]: {},
  [state.UNFILTERED_DATA]: [],
  [state.FILTERED_DATA]: [],
  [state.INPUT_VARIABLES]: [],
  [state.OUTPUT_VARIABLES]: [],
  [state.CROSS_FILTER]: null,
  [state.DIMENSIONS]: {},
  [state.PVALS]: [],
  [state.PVAL_THRESHOLD]: 'None',
  [state.QUERIES]: {},
};
