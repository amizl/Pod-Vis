import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_NOTIFICATION](state, notification) {
    state[stateTypes.NOTIFICATION] = notification;
  },
  [mutations.SET_NOTIFY](state, notify) {
    state[stateTypes.NOTIFY] = notify;
  },
};
