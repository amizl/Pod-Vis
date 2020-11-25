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
  [state.PVALS_REQUEST_NUM]: 0,
  [state.PVALS_REQUEST_DELAY_SECS]: 1,
  [state.PVALS_REQUEST_STATUS]: null,
  [state.PVAL_THRESHOLD]: 0.05,
  [state.HIGHLIGHTED_SUBSET]: 'cohort',
  [state.QUERIES]: {},
  [state.COMPARISON_MEASURE]: 'Last Visit',
  [state.USE_LONG_SCALE_NAMES]: false,
};
