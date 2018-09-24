import * as firebase from 'firebase';
import { actions, mutations } from './types';

export default {
  [actions.FETCH_DATASETS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    firebase
      .firestore()
      .collection('datasets')
      .get()
      .then((querySnapshot) => {
        const datasets = querySnapshot
          .docs
          .map(doc => doc.data());

        commit(mutations.SET_DATASETS, datasets);
        commit(mutations.SET_LOADING, false);
      })
      /* eslint-disable-next-line */
      .catch((error) => {
        // TODO
      });
  },
  [actions.SELECT_DATASETS]({ commit }, payload) {
    console.log(payload);
    commit(mutations.SET_SELECTED_DATASETS, payload);
  },
};
