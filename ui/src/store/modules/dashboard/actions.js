import {
  SuccessNotification,
  // ErrorNotification,
} from '@/store/modules/notifications/notifications';

import { actions, mutations } from './types';

export default {
  [actions.ADD_DATASET_TO_PROFILE]({ commit, dispatch }, payload) {
    const notification = new SuccessNotification('Added to profile.');
    dispatch(notification.dispatch, notification, { root: true });
    commit(mutations.SET_DATASETS, Array(payload));
  },
};
