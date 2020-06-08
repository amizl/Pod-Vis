import { state } from './types';

export default {
  [state.IS_LOADING]: false,
  [state.COLLECTION]: {},
  [state.COLLECTION_SUMMARIES]: null,
  [state.FIRST_VISIT]: null,
  [state.LAST_VISIT]: null,
  [state.VISIT_VARIABLE]: 'Visit Event',
  [state.TIMES_BETWEEN_VISITS]: null,
};
