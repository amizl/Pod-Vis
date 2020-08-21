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
      const { data } = await axios.get(
        '/api/projects?include=studies&include=num_subjects'
      );
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

      commit(mutations.ADD_COLLECTION, data.collection);
      commit(mutations.SET_LOADING, false);

      const notification = new SuccessNotification(
        'Study Dataset successfully saved.'
      );

      commit(mutations.CLEAR_SELECTED_DATASETS);
      dispatch(notification.dispatch, notification, { root: true });
      return new Promise(resolve => {
        resolve(data.collection);
      });
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
      const { data } = await axios.get(
        '/api/collections?include=cohort_counts&include=variables&include=studies'
      );
      data.collections.forEach(c => {
        c.date_generated_epoch = new Date(c.date_generated).getTime();
        c.has_visits_set = true;
        c.observation_variables.forEach(v => {
          if (
            (v.first_visit_event == null && v.first_visit_num == null) ||
            (v.last_visit_event == null && v.last_visit_num == null)
          ) {
            c.has_visits_set = false;
          }
        });
      });
      data.collections.sort((a, b) => {
        return b.date_generated_epoch - a.date_generated_epoch;
      });
      commit(mutations.SET_COLLECTIONS, data.collections);
    } catch (err) {
      const notification = new ErrorNotification(err);
      dispatch(notification.dispatch, notification, { root: true });
    }

    commit(mutations.SET_LOADING, false);
  },
  /**
   * Fetch a single collection.
   * @param {Object} context
   */
  async [actions.FETCH_COLLECTION]({ commit, dispatch }, collectionId) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        '/api/collections/' +
          collectionId +
          '?include=cohorts&include=variables&include=studies'
      );
      var c = data.collection;
      c.date_generated_epoch = new Date(c.date_generated).getTime();
      c.has_visits_set = true;
	c.subject_variables.forEach(v => {
          if (v.ontology.label == "Dataset") {
            v.ontology.category = "Dataset";
          }
	});
      c.observation_variables.forEach(v => {
        if (
          (v.first_visit_event == null && v.first_visit_num == null) ||
          (v.last_visit_event == null && v.last_visit_num == null)
        ) {
          c.has_visits_set = false;
        }
      });
      commit(mutations.SET_COLLECTION, c);
    } catch (err) {
      const notification = new ErrorNotification(err);
      dispatch(notification.dispatch, notification, { root: true });
    }
    commit(mutations.SET_LOADING, false);
  },
  async [actions.DELETE_COLLECTION]({ commit, dispatch }, collectionId) {
    commit(mutations.SET_LOADING, true);

    try {
      await axios.delete(`/api/collections/${collectionId}`);
      commit(mutations.DELETE_COLLECTION, collectionId);
      const notification = new SuccessNotification(
        'Study Dataset successfully deleted.'
      );
      dispatch(notification.dispatch, notification, { root: true });
    } catch (err) {
      const notification = new ErrorNotification(err);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
};
