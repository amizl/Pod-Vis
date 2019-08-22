import Vue from 'vue';
import * as crossfilter from 'crossfilter2';
import { mutations, state as stateTypes } from './types';

export default {
  /**
   * Set cohorts mutation.
   * @param {*} state
   * @param {*} cohorts
   */
  [mutations.SET_COHORTS](state, cohorts) {
    state[stateTypes.COHORTS] = cohorts;
  },
  /**
   * Set cohort mutation.
   * @param {*} state
   * @param {*} cohort
   */
  [mutations.SET_COHORT](state, cohort) {
    state[stateTypes.COHORT] = cohort;
  },
  /**
   * Add cohort to cohorts.
   * @param {*} state
   * @param {*} cohort
   */
  [mutations.ADD_COHORT](state, cohort) {
    state[stateTypes.COHORTS] = [...state[stateTypes.COHORTS], cohort];
  },
  /**
   * Remove cohort from cohorts.
   * @param {*} state
   * @param {*} cohortID
   */
  [mutations.REMOVE_COHORT](state, cohortID) {
    state[stateTypes.COHORTS] = state[stateTypes.COHORTS].filter(
      cohort => cohort.id !== cohortID
    );
  },
  /**
   * Set loading mutation.
   * @param {Object} state
   * @param {Boolean} isLoading Flag whether or not we are waiting on data.
   */
  [mutations.SET_LOADING](state, isLoading) {
    state[stateTypes.IS_LOADING] = isLoading;
  },
  /**
   * Set collection mutation.
   * @param {Object} state Global cohort manager state.
   * @param {Object} collection
   */
  [mutations.SET_COLLECTION](state, collection) {
    state[stateTypes.COLLECTION] = collection;
  },
  /**
   * Add input variable to our array of variables.
   * @param {Object} state Global cohort manager state.
   * @param {Object} variable Input variable
   */
  [mutations.ADD_INPUT_VARIABLE](state, variable) {
    state[stateTypes.INPUT_VARIABLES].push(variable);
  },
  /**
   * Remove input variable from array.
   * @param {Object} state Global cohort manager state
   * @param {Object} variable Input variable to remove
   */
  [mutations.REMOVE_INPUT_VARIABLE](state, variable) {
    const inputVariables = state[stateTypes.INPUT_VARIABLES];
    const indexToRemove = inputVariables.findIndex(
      inputVar => inputVar.id === variable.id
    );
    Vue.delete(inputVariables, indexToRemove);
  },
  /**
   * Add output variable to our array of variables.
   * @param {Object} state Global cohort manager state.
   * @param {Object} variable Output variable
   */
  [mutations.ADD_OUTPUT_VARIABLE](state, variable) {
    state[stateTypes.OUTPUT_VARIABLES].push(variable);
  },
  /**
   * Remove output variable from array.
   * @param {Object} state Global cohort manager state
   * @param {Object} variable Output variable to remove
   */
  [mutations.REMOVE_OUTPUT_VARIABLE](state, variable) {
    const outputVariables = state[stateTypes.OUTPUT_VARIABLES];
    const indexToRemove = outputVariables.findIndex(
      inputVar => inputVar.id === variable.id
    );
    Vue.delete(outputVariables, indexToRemove);
  },
  /**
   * Initialize crossfilter.
   *
   * Crossfilter assists with managing filters across dimensions
   * and makes sure we don't send dimension filters to chart that is
   * using that dimension.
   *
   * @param {Object} state Global cohort manager state.
   * @param {*} data Patient records. Each index is a patient
   * with all appropriate metadata. (Demographics/Outcomes)
   */
  [mutations.INITIALIZE_CROSS_FILTER](state, data) {
    const xf = crossfilter(data);
    state[stateTypes.CROSS_FILTER] = xf;
    // Unfiltered data should only be initialized once
    state[stateTypes.UNFILTERED_DATA] = xf.all();
  },
  /**
   * Filters were added, update our filtered data.
   *
   * Crossfilter manages its own state and Vue cant
   * know about this to be reactive. What vue can track is
   * arrays, so whenever we update crossfilter, we want to
   * set our reactive array to our new crossfilter filtered
   * array. When this reactive array detects changes, it will
   * then propogate those changes to components using it.
   *
   * @param {Object} state Global cohort manager state.
   */
  [mutations.UPDATE_FILTERED_DATA](state) {
    const xf = state[stateTypes.CROSS_FILTER];
    state[stateTypes.FILTERED_DATA] = xf.allFiltered();
  },
  /**
   * Set input variables.
   * @param {*} state
   * @param {*} newInputVariables
   */
  [mutations.SET_INPUT_VARIABLES](state, newInputVariables) {
    state[stateTypes.INPUT_VARIABLES] = newInputVariables;
  },
  /**
   * Set output variables.
   * @param {*} state
   * @param {*} newOutputVariables
   */
  [mutations.SET_OUTPUT_VARIABLES](state, newOutputVariables) {
    state[stateTypes.OUTPUT_VARIABLES] = newOutputVariables;
  },
  /**
   * Add a dimension to crossfilter.
   *
   * We use dimensions to add filters.
   * @param {Object} state Global cohort manager state.
   * @param {String} dimensionName The name of our dimension. ("Sex")
   */
  [mutations.ADD_DIMENSION](state, { dimensionName, accessor }) {
    const xf = state[stateTypes.CROSS_FILTER];
    const dimensions = state[stateTypes.DIMENSIONS];
    // Dimensions are stateful and we want to make sure we are not initializing
    // dims that have been already initialized.
    // https://github.com/crossfilter/crossfilter/wiki/API-Reference#Dimension
    if (!(dimensionName in dimensions)) {
      const dimension = xf.dimension(accessor);
      Vue.set(dimensions, dimensionName, dimension);
    }
  },
  /**
   * Add filter to dimension
   * @param {Object} state Global cohort manager state.
   * @param {Object} filter An object with dimension and filter keys.
   */
  [mutations.ADD_FILTER](state, { dimension, filter }) {
    const dimensions = state[stateTypes.DIMENSIONS];
    const dim = dimensions[dimension];
    dim.filterFunction(filter);
  },
  /**
   * Remove dimension.
   * @param {Object} state
   * @param {String} dimensionName
   */
  [mutations.REMOVE_DIMENSION](state, dimensionName) {
    const dimensions = state[stateTypes.DIMENSIONS];
    const dimension = dimensions[dimensionName];
    // https://github.com/crossfilter/crossfilter/wiki/API-Reference#dimension_dispose
    dimension.dispose();
  },
  /**
   * Clear a dimension's filter.
   * @param {Object} state
   * @param {Object} dimension
   */
  [mutations.CLEAR_FILTER](state, { dimension }) {
    const dimensions = state[stateTypes.DIMENSIONS];
    const dim = dimensions[dimension];
    if (typeof dim !== 'undefined') {
	dim.filterAll();
    }
  },
  /**
   * Set pvals
   * @param {Object} state
   * @param {Array} pvals Array of objects with a pval and its corresponding outcome measure.
   */
  [mutations.SET_PVALS](state, pvals) {
    state[stateTypes.PVALS] = pvals;
  },
  /**
   * Set query for particular dimension.
   * @param {Object} state
   * @param {Object} query Object with the keys, param, operator, value that represents a filter
   */
  [mutations.SET_QUERY](state, { dimension, query }) {
    const queries = state[stateTypes.QUERIES];

    if (!(dimension in queries)) {
      Vue.set(queries, dimension, []);
    }
    // Bar charts can have multiple queries (more than one study selected)
    // while histograms will just have a single range query.
    const dimensionQueries = Array.isArray(query) ? query : [query];
    queries[dimension] = dimensionQueries;
  },
  /**
   * Clear query for particular dimension.
   * @param {Object} state
   * @param {String} dimension
   */
  [mutations.CLEAR_QUERY](state, dimension) {
    const queries = state[stateTypes.QUERIES];

    if (dimension in queries) {
      Vue.delete(queries, dimension);
    }
  },
  /**
   * Reset cohort data back to orignal state.
   * @param {Object} state
   */
  [mutations.RESET_COHORTS](state) {
    state[stateTypes.COHORTS] = [];
  },
  /**
   * Reset is loading back to original state.
   * @param {Object} state
   */
  [mutations.RESET_IS_LOADING](state) {
    state[stateTypes.IS_LOADING] = false;
  },
  /**
   * Reset collection back to original state.
   * @param {Object} state
   */
  [mutations.RESET_COLLECTION](state) {
    state[stateTypes.COLLECTION] = {};
  },
  /**
   * Reset unfiltered data back to original state.
   * @param {Object} state
   */
  [mutations.RESET_UNFILTERED_DATA](state) {
    state[stateTypes.UNFILTERED_DATA] = [];
  },
  /**
   * Reset filtered data back to original state.
   * @param {Object} state
   */
  [mutations.RESET_FILTERED_DATA](state) {
    state[stateTypes.FILTERED_DATA] = [];
  },
  /**
   * Reset input variables back to original state;
   * @param {Object} state
   */
  [mutations.RESET_INPUT_VARIABLES](state) {
    state[stateTypes.INPUT_VARIABLES] = [];
  },
  /**
   * Reset output variables back to original state.
   * @param {Object} state
   */
  [mutations.RESET_OUTPUT_VARIABLES](state) {
    state[stateTypes.OUTPUT_VARIABLES] = [];
  },
  /**
   * Reset crossfilter back to original state.
   * @param {Object} state
   */
  [mutations.RESET_CROSS_FILTER](state) {
    state[stateTypes.CROSS_FILTER] = null;
  },
  /**
   * Reset dimensions back to original state.
   * @param {Object} state
   */
  [mutations.RESET_DIMENSIONS](state) {
    state[stateTypes.DIMENSIONS] = {};
  },
  /**
   * Reset pvals back to original state.
   * @param {Object} state
   */
  [mutations.RESET_PVALS](state) {
    state[stateTypes.PVALS] = [];
  },
  /**
   * Reset queries back to original state.
   * @param {Object} state
   */
  [mutations.RESET_QUERIES](state) {
    state[stateTypes.QUERIES] = {};
  },
};
