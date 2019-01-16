import Vue from 'vue';
import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_DATASET](state, payload) {
    state[stateTypes.DATASET] = payload;
  },
  [mutations.SET_LOADING](state, payload) {
    state[stateTypes.IS_LOADING] = payload;
  },
  [mutations.SET_COHORT_SELECTION](state, payload) {
    const { axis, scaled } = payload;
    const obj = state[stateTypes.COHORT_SELECTION];

    Vue.set(obj, axis, scaled);
  },
};
