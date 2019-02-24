import { getters, state as stateTypes } from './types';

export default {
  [getters.NOTIFICATION_EXISTS]: state =>
    state[stateTypes.NOTIFICATION] !== null,
};
