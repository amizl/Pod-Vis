import axios from 'axios';
import { ErrorNotification } from '@/store/modules/notifications/notifications';
import { actions, mutations, state as stateTypes } from './types';

export default {
  async [actions.FETCH_COHORTS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/cohorts');
      commit(mutations.SET_COHORTS, data.cohorts);
    } catch (err) {
      // TODO
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  async [actions.FETCH_COLLECTION]({ commit, dispatch }, collectionId) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        `/api/collections/${collectionId}?include=studies&include=variables`
      );
      commit(mutations.SET_COLLECTION, data.collection);
    } catch ({ response }) {
      // Something went wrong...
      // user didn't have access to collection? collection not found?
      // Display notification via notifcation snackbar? Reroute? Display msg in cohort manager?
      // TODO...

      // Currently displays error message.
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  async [actions.FETCH_DATA]({ commit, dispatch, state }) {
    commit(mutations.SET_LOADING, true);
    const collection = state[stateTypes.COLLECTION];

    try {
      const { data } = await axios.get(
        `/api/cohort-manager?collection=${collection.id}`
      );
      commit(mutations.SET_DATA, data.data);
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  [actions.ADD_INPUT_VARIABLE]({ commit }, inputVariable) {
    commit(mutations.ADD_INPUT_VARIABLE, inputVariable);
  },
  [actions.REMOVE_INPUT_VARIABLE]({ commit }, inputVariable) {
    commit(mutations.REMOVE_INPUT_VARIABLE, inputVariable);
  },
  [actions.SET_INPUT_VARIABLES]({ commit }, newInputVariables) {
    commit(mutations.SET_INPUT_VARIABLES, newInputVariables);
  },
};
