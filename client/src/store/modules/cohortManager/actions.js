import * as firebase from 'firebase';
import store from '@/store';
import { actions, mutations } from './types';

export default {
  [actions.FETCH_COHORTS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    firebase
      .firestore()
      .collection('users')
      .doc(store.state.auth.user)
      .collection('cohorts')
      .get()
      .then((querySnapshot) => {
        const cohorts = querySnapshot
          .docs
          .map(doc => doc.data());
        commit(mutations.SET_COHORTS, cohorts);
        commit(mutations.SET_LOADING, false);
      });
  },
};
