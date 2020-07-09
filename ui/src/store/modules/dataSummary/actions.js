import axios from 'axios';
import { nest } from 'd3-collection';
import {
  ErrorNotification,
  SuccessNotification,
} from '@/store/modules/notifications/notifications';
import { makeHierarchy, getObservationVariableIds } from '@/utils/helpers';
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

      // update first/last visit info
      var firstVisits = {};
      var lastVisits = {};
      var visitVar = null;

      data.collection.observation_variables.forEach(ov => {
        if (ov['first_visit_event']) {
          visitVar = 'Visit Event';
          firstVisits[ov['ontology']['id']] = ov['first_visit_event'];
          lastVisits[ov['ontology']['id']] = ov['last_visit_event'];
        } else {
          visitVar = 'Visit Number';
          firstVisits[ov['ontology']['id']] = ov['first_visit_num'];
          lastVisits[ov['ontology']['id']] = ov['last_visit_num'];
        }
      });
      commit(mutations.SET_VISIT_VARIABLE, visitVar);
      commit(mutations.SET_FIRST_VISITS, firstVisits);
      commit(mutations.SET_LAST_VISITS, lastVisits);

      const observationVariables = makeHierarchy(
        data.collection.observation_variables
      );
      data.collection.observation_variables_list =
        data.collection.observation_variables;

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
  [actions.SET_FIRST_VISITS]({ commit }, newFirstVisits) {
    commit(mutations.SET_FIRST_VISITS, newFirstVisits);
  },
  [actions.SET_LAST_VISITS]({ commit }, newLastVisits) {
    commit(mutations.SET_LAST_VISITS, newLastVisits);
  },
  [actions.SET_VISIT_VARIABLE]({ commit }, newVisitVar) {
    commit(mutations.SET_FIRST_VISITS, {});
    commit(mutations.SET_LAST_VISITS, {});
    commit(mutations.SET_VISIT_VARIABLE, newVisitVar);
  },
  // set all variables to same first/last visit
  [actions.SET_FIRST_VISIT]({ commit, state }, newFirstVisit) {
    var collection = state[stateTypes.COLLECTION];
    var firstVisits = {};
    getObservationVariableIds(collection).forEach(oid => {
      firstVisits[oid] = newFirstVisit;
    });
    commit(mutations.SET_FIRST_VISITS, firstVisits);
  },
  [actions.SET_LAST_VISIT]({ commit, state }, newLastVisit) {
    var collection = state[stateTypes.COLLECTION];
    var lastVisits = {};
    getObservationVariableIds(collection).forEach(oid => {
      lastVisits[oid] = newLastVisit;
    });
    commit(mutations.SET_LAST_VISITS, lastVisits);
  },
  async [actions.FETCH_TIMES_BETWEEN_VISITS]({ commit, dispatch, state }) {
    var collection = state[stateTypes.COLLECTION];
    var visitVariable = state[stateTypes.VISIT_VARIABLE];
    var firstVisits = state[stateTypes.FIRST_VISITS];
    var lastVisits = state[stateTypes.LAST_VISITS];

    if (collection && visitVariable && firstVisits && lastVisits) {
      var query_by =
        visitVariable === 'Visit Event' ? 'visit_event' : 'visit_num';
      var request_url =
        '/api/collections/time_between_visits/' +
        collection.id +
        '?query_by=' +
        query_by;

      var first_visits_l = [];
      var last_visits_l = [];
      var obs_var_ids_l = [];

      // comma-separated lists for first_visits, last_visits, obs_var_ids
      getObservationVariableIds(collection).forEach(o => {
        obs_var_ids_l.push(o);
        first_visits_l.push(firstVisits[o]);
        last_visits_l.push(lastVisits[o]);
      });

      request_url = request_url + '&obs_var_ids=' + obs_var_ids_l.join(',');
      request_url = request_url + '&first_visits=' + first_visits_l.join(',');
      request_url = request_url + '&last_visits=' + last_visits_l.join(',');

      const { data } = await axios.get(request_url);
      // TODO -
      if (
        data['query_by'] === query_by
        // &&       data['visit1'] == firstVisit &&
        //        data['visit2'] == lastVisit
      ) {
        commit(mutations.SET_TIMES_BETWEEN_VISITS, data['times']);
        var ns = 0;
        data['times'].forEach(t => {
          if (t['is_first']) {
            ns += t.n_subjects;
          }
        });
        commit(mutations.SET_NUM_SELECTED_SUBJECTS, ns);
      }
    }
  },
  async [actions.SAVE_FIRST_AND_LAST_VISITS](
    { commit, dispatch, state },
    { variableVisits }
  ) {
    const { collection } = state;

    try {
      const { data } = await axios.post(
        '/api/collections/' + collection.id + '/observation_visits',
        {
          variable_visits: variableVisits,
        }
      );
      //      commit(mutations.ADD_COHORT, data.cohort);
    } catch ({ response }) {
      const notification = new ErrorNotification(response.data.error);
      dispatch(notification.dispatch, notification, { root: true });
    }
  },
};
