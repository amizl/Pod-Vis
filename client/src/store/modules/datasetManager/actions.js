import * as firebase from 'firebase';
import store from '../../../store/';
import { actions, mutations } from './types';

export default {
  [actions.FETCH_DATASETS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    firebase
      .firestore()
      .collection('datasets')
      .get()
      .then(querySnapshot => {
        const datasets = querySnapshot.docs.map(doc => {
          const dataset = doc.data();
          return {
            id: doc.id,
            ...dataset,
          };
        });

        commit(mutations.SET_DATASETS, datasets);
        commit(mutations.SET_LOADING, false);
      })
      /* eslint-disable-next-line */
      .catch((error) => {
        // TODO
      });
  },
  [actions.SELECT_DATASETS]({ commit }, payload) {
    commit(mutations.SET_SELECTED_DATASETS, payload);
  },
  [actions.ADD_SELECTED_DATASETS_TO_COHORTS]({ commit }, payload) {
    commit(mutations.SET_LOADING, true);

    payload.forEach(dataset => {
      firebase
        .firestore()
        .collection('users')
        .doc(store.state.auth.user)
        .collection('cohorts')
        .add(dataset)
        .then(() => {
          commit(mutations.SET_LOADING, false);
        });
    });
  },
};
