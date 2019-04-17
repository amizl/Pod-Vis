import {
  SuccessNotification,
  ErrorNotification,
} from '@/store/modules/notifications/notifications';
import axios from 'axios';
import { actions, mutations } from './types';

export default {
  async [actions.FETCH_DATASETS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/projects?include=studies');
      const projects = data.projects;

      const datasets = projects
        .map(project =>
          project.studies.map(study => ({
            project_name: project.project_name,
            ...study,
          }))
        )
        .flat();
      commit(mutations.SET_DATASETS, datasets);
    } catch (err) {
      // TODO
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
      await axios.post('/api/collections', {
        label: payload.collectionName,
        study_ids: payload.datasetIds,
        variables: payload.variables,
      });
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
};
