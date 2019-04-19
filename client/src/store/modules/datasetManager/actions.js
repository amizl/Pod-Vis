import {
  SuccessNotification,
  ErrorNotification,
} from '@/store/modules/notifications/notifications';
import axios from 'axios';
import { actions, mutations } from './types';

export default {
  /**
   * Fetch all datasets/studies from server.
   * @param {Object} Context
   */
  async [actions.FETCH_DATASETS]({ commit, dispatch }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/projects?include=studies');
      const datasets = data.projects
        .map(project =>
          project.studies.map(study => ({
            project_name: project.project_name,
            ...study,
          }))
        )
        .flat();
      commit(mutations.SET_DATASETS, datasets);
    } catch (err) {
      const notification = new ErrorNotification(err);
      dispatch(notification.dispatch, notification, { root: true });
      commit(mutations.SET_LOADING, false);
    }
    commit(mutations.SET_LOADING, false);
  },
  [actions.SELECT_DATASETS]({ commit }, selectedDatasets) {
    commit(mutations.SET_SELECTED_DATASETS, selectedDatasets);
  },
  /**
   * Save collection to the database.
   * @param {Object} context
   * @param {Object} payload
   */
  async [actions.SAVE_COLLECTION]({ commit, dispatch }, payload) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.post('/api/collections', {
        label: payload.collectionName,
        study_ids: payload.datasetIds,
        variables: payload.variables,
      });
      console.log(data);
      commit(mutations.ADD_COLLECTION, data.collection);
      commit(mutations.SET_LOADING, false);

      const notification = new SuccessNotification(
        'Collection successfully saved.'
      );
      dispatch(notification.dispatch, notification, { root: true });

      return new Promise(resolve => resolve());
    } catch (err) {
      const notification = new ErrorNotification(err);
      dispatch(notification.dispatch, notification, { root: true });
      commit(mutations.SET_LOADING, false);
      return new Promise((resolve, reject) => reject());
    }
  },
  /**
   * Fetch all of user's collections.
   * @param {Object} context
   */
  async [actions.FETCH_COLLECTIONS]({ commit, dispatch }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/collections');
      commit(mutations.SET_COLLECTIONS, data.collections);
    } catch (err) {
      const notification = new ErrorNotification(err);
      dispatch(notification.dispatch, notification, { root: true });
    }

    commit(mutations.SET_LOADING, false);
  },
};
