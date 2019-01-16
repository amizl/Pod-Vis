import * as firebase from 'firebase';
// import store from '@/store';
import { actions, mutations } from './types';

export default {
  async [actions.FETCH_DATASET]({ commit }, payload) {
    commit(mutations.SET_LOADING, true);
    firebase
      .firestore()
      .collection('datasets')
      .doc(payload)
      .get()
      .then(querySnapshot => {
        const dataset = querySnapshot.data();
        commit(mutations.SET_DATASET, dataset);
        commit(mutations.SET_LOADING, false);
      });
  },
  [actions.SET_COHORT_SELECTION]({ commit }, payload) {
    commit(mutations.SET_COHORT_SELECTION, payload);
  },
  // firebase
  //   .firestore()
  //   .collection('users')
  //   .doc(store.state.auth.user)
  //   .collection('cohorts')
  //   .get()
  //   .then(querySnapshot => {
  //     const cohorts = querySnapshot.docs.map(doc => doc.data());
  //     commit(mutations.SET_COHORTS, cohorts);
  //     commit(mutations.SET_LOADING, false);
  //   });
};
