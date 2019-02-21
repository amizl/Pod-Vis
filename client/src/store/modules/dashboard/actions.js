import * as firebase from 'firebase';
import store from '@/store';
import { actions, mutations } from './types';

export default {
  [actions.FETCH_DATASETS]({ commit }, payload) {
    commit(mutations.SET_LOADING, true);
    const { user } = store.state.auth;

    firebase
      .firestore()
      .collection('users')
      .doc(user)
      .collection('datasets')
      .get()
      .then(querySnapshot => {
        const datasets = querySnapshot.docs.map(doc => doc.data());

        commit(mutations.SET_DATASETS, datasets);
        commit(mutations.SET_LOADING, false);
      });
  },
  [actions.ADD_DATASET_TO_PROFILE]({ commit }, payload) {
    return firebase
      .firestore()
      .collection('users')
      .doc(store.state.auth.user)
      .collection('datasets')
      .add(payload)
      .then(() => {
        commit(mutations.SET_DATASETS, Array(payload));
      });
  },
  [actions.REMOVE_DATASET_FROM_PROFILE]({ commit }, payload) {
    // TODO
  },
};
