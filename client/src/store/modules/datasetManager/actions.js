import * as firebase from 'firebase';
import axios from 'axios';
import store from '../../../store/';
import { actions, mutations } from './types';

export default {
  async [actions.FETCH_DATASETS]({ commit }) {
    commit(mutations.SET_LOADING, true);

    try {
      const { data } = await axios.get('/api/projects');
      const projects = data.projects;

      const datasets = projects
        .map(project =>
          project.studies.map(study => ({
            ...study,
            study_name: `${project.project_name}: ${study.study_name}`,
          }))
        )
        .flat();
      commit(mutations.SET_DATASETS, datasets);
    } catch (err) {
      // TODO
    }
    commit(mutations.SET_LOADING, false);
    // firebase
    //   .firestore()
    //   .collection('datasets')
    //   .get()
    //   .then(querySnapshot => {
    //     const datasets = querySnapshot.docs.map(doc => {
    //       const dataset = doc.data();
    //       return {
    //         id: doc.id,
    //         ...dataset,
    //       };
    //     });

    //     commit(mutations.SET_DATASETS, datasets);
    //     commit(mutations.SET_LOADING, false);
    //   })
    //   /* eslint-disable-next-line */
    //   .catch((error) => {
    //     // TODO
    //   });
  },
  [actions.SELECT_DATASETS]({ commit }, selectedDatasets) {
    commit(mutations.SET_SELECTED_DATASETS, selectedDatasets);
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
