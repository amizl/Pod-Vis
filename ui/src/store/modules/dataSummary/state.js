import { state } from './types';

export default {
  [state.IS_LOADING]: false,
  [state.COLLECTION]: {},
  [state.COLLECTION_SUMMARIES]: null,
  [state.FIRST_VISITS]: {},
  [state.LAST_VISITS]: {},
  [state.VISIT_VARIABLE]: 'Visit Event',
  [state.TIMES_BETWEEN_VISITS]: null,
  [state.NUM_SELECTED_SUBJECTS]: 0,
};
