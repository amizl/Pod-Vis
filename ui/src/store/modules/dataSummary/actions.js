import axios from 'axios';
import { nest } from 'd3-collection';
import {
  ErrorNotification,
  SuccessNotification,
} from '@/store/modules/notifications/notifications';
import { makeHierarchy, getInputVariablesFromQueries } from '@/utils/helpers';
import {
  actions,
  getters as getterTypes,
  mutations,
  state as stateTypes,
} from './types';

export default {
  async [actions.FETCH_COLLECTION]({ commit, dispatch }, collectionId) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        `/api/collections/${collectionId}?include=studies&include=variables`
      );
      // massage collection data... here

      const subjectVariables = makeHierarchy(data.collection.subject_variables);

      subjectVariables.forEach(subjectVariable => {
        subjectVariable.children.forEach(child => (child['type'] = 'subject'));
      });

      const observationVariables = makeHierarchy(
        data.collection.observation_variables
      );
      // TODO:
      // These fields are hard-coded and will inevitably need to be changed.
      // For example, firstVisit and lastVisit are stored in the database as
      //  left_y_axis and right_y_axis when queries are saved. This is because
      //  eventually we want to allow the user to specify the visit number rather
      //  than hard-coding first and last.
      observationVariables.forEach(observationVariable => {
        observationVariable.children.forEach(child => {
          child['type'] = 'observation';
          child['children'] = [
            {
              ...child,
              id: `firstVisit-${child.id}`,
              parentID: child.id,
              parentLabel: child.label,
              label: 'First Visit',
            },
            {
              ...child,
              id: `lastVisit-${child.id}`,
              parentID: child.id,
              parentLabel: child.label,
              label: 'Last Visit',
            },
            {
              ...child,
              id: `change-${child.id}`,
              parentID: child.id,
              parentLabel: child.label,
              label: 'Change',
            },
            {
              ...child,
              id: `roc-${child.id}`,
              parentID: child.id,
              parentLabel: child.label,
              label: 'Rate of Change',
            },
          ];
        });
      });

      data.collection.subject_variables = subjectVariables;
      data.collection.observation_variables = observationVariables;
      commit(mutations.SET_COLLECTION, data.collection);
    } catch ({ response }) {
      // Something went wrong...
      // user didn't have access to collection? collection not found?
      // Display notification via notifcation snackbar? Reroute? Display msg in cohort manager?
      // TODO...

      // Currently displays error message.
      const notification = new ErrorNotification(response);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  async [actions.FETCH_COLLECTION_SUMMARIES](
    { commit, dispatch },
    collectionId
  ) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get(
        `/api/collections/obs_summaries/${collectionId}`
      );

      // massage collection observation summary data... here
      commit(mutations.SET_COLLECTION_SUMMARIES, data['summaries']);
    } catch ({ response }) {
      // Something went wrong...
      // user didn't have access to collection? collection not found?
      // Display notification via notifcation snackbar? Reroute? Display msg in cohort manager?
      // TODO...

      // Currently displays error message.
      const notification = new ErrorNotification(response);
      dispatch(notification.dispatch, notification, { root: true });
    } finally {
      commit(mutations.SET_LOADING, false);
    }
  },
  [actions.SET_FIRST_VISIT]({ commit }, newFirstVisit) {
    commit(mutations.SET_FIRST_VISIT, newFirstVisit);
  },
  [actions.SET_LAST_VISIT]({ commit }, newLastVisit) {
    commit(mutations.SET_LAST_VISIT, newLastVisit);
  },
  [actions.SET_VISIT_VARIABLE]({ commit }, newVisitVar) {
    commit(mutations.SET_FIRST_VISIT, null);
    commit(mutations.SET_LAST_VISIT, null);
    commit(mutations.SET_VISIT_VARIABLE, newVisitVar);
  },
  async [actions.FETCH_TIMES_BETWEEN_VISITS]({ commit, dispatch, state }) {
    var collection = state[stateTypes.COLLECTION];
    var visitVariable = state[stateTypes.VISIT_VARIABLE];
    var firstVisit = state[stateTypes.FIRST_VISIT];
    var lastVisit = state[stateTypes.LAST_VISIT];
    if (collection && visitVariable && firstVisit && lastVisit) {
      var query_by =
        visitVariable === 'Visit Event' ? 'visit_event' : 'visit_num';
      var request_url =
        '/api/collections/time_between_visits/' +
        collection.id +
        '?query_by=' +
        query_by +
        '&visit1=' +
        firstVisit +
        '&visit2=' +
        lastVisit;

      const { data } = await axios.get(request_url);
      if (
        data['query_by'] === query_by &&
        data['visit1'] == firstVisit &&
        data['visit2'] == lastVisit
      ) {
        commit(mutations.SET_TIMES_BETWEEN_VISITS, data['times']);
      }
    }

    //      try {
    //      const { data } = await axios.get(
    //        `/api/collections/${collectionId}?include=studies&include=variables`
    //      );
  },
};
