import Vue from 'vue';
import { mutations, state as stateTypes } from './types';

export default {
  [mutations.SET_COHORTS](state, cohorts) {
    state[stateTypes.COHORTS] = cohorts;
  },
  [mutations.SET_LOADING](state, isLoading) {
    state[stateTypes.IS_LOADING] = isLoading;
  },
  [mutations.SET_COLLECTION](state, collection) {
    state[stateTypes.COLLECTION] = collection;
  },
  [mutations.SET_DATA](state, data) {
    state[stateTypes.DATA] = data;
  },
  [mutations.ADD_INPUT_VARIABLE](state, variable) {
    state[stateTypes.INPUT_VARIABLES].push(variable);
  },
  [mutations.REMOVE_INPUT_VARIABLE](state, variable) {
    const inputVariables = state[stateTypes.INPUT_VARIABLES];
    const index = inputVariables.findIndex(
      inputVar => inputVar.id === variable.id
    );
    Vue.delete(inputVariables, index);
  },
  [mutations.SET_INPUT_VARIABLES](state, newInputVariables) {
    state[stateTypes.INPUT_VARIABLES] = newInputVariables;
  },
};
