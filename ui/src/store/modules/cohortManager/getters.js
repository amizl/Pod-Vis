import { getters, state as stateTypes } from './types';

export default {
  [getters.HAS_USER_FILTERED_INPUT_VARIABLES]: state => {
    const NO_QUERIES = 0;
    const queries = state[stateTypes.QUERIES];

    return (
      Object.entries(queries).length > NO_QUERIES &&
      queries.constructor === Object
    );
  },
};
