import { nest } from 'd3-collection';
import { getInputVariablesFromQueries } from '@/utils/helpers';
import { getters, state as stateTypes } from './types';

export default {
  [getters.HAS_USER_FILTERED_INPUT_VARIABLES]: state => {
    const queries = state[stateTypes.QUERIES];
    const inputVars = state[stateTypes.INPUT_VARIABLES];
    const q2m = getInputVariablesFromQueries(queries, inputVars);
    return q2m.length > 0;
  },
  [getters.HAS_USER_FILTERED_OUTPUT_VARIABLES]: state => {
    const queries = state[stateTypes.QUERIES];
    const inputVars = state[stateTypes.INPUT_VARIABLES];
    var nQueries = Object.entries(queries).length;
    const q2m = getInputVariablesFromQueries(queries, inputVars);
    var nInputVarQueries = q2m.length;
    return nInputVarQueries < nQueries;
  },
  [getters.HAS_USER_SELECTED_COHORT]: state => {
    const cohort = state[stateTypes.COHORT];
    if (cohort.id == null || cohort.id < 0) {
      return false;
    }
    return true;
  },
  [getters.FIND_COHORT_QUERY]: state => dimensionName =>
    state.cohort.queries == null
      ? []
      : state.cohort.queries.filter(query => {
          const inputVariable = query.input_variable;
          // Need to safely access correct attribute
          if (inputVariable.study) {
            return inputVariable.study.label === dimensionName;
          } else if (inputVariable.observation_ontology) {
            // TODO: This needs to be refactored. Dimensions are currently
            // keyed strangely and needs to be better named for an easier
            // mapping then having to format labels like this...
            const observationLabel = inputVariable.observation_ontology.label;
            const dimLabel = inputVariable.dimension_label;
            let newLabel = '';
            if (dimLabel === 'change') {
              newLabel = `${observationLabel} - Change`;
            } else if (dimLabel === 'roc') {
              newLabel = `${observationLabel} - Rate of Change`;
            } else if (dimLabel === 'left_y_axis') {
              newLabel = `${observationLabel} - First Visit`;
            } else if (dimLabel === 'right_y_axis') {
              newLabel = `${observationLabel} - Last Visit`;
            }
            return newLabel === dimensionName;
          }
          return inputVariable.subject_ontology.label === dimensionName;
        }),
  //  [getters.FIND_COHORT_STUDY_INPUT_VARIABLES]: state => {
  //    return !state.cohort.input_variables
  //      ? []
  //      : state.cohort.input_variables
  //          .filter(variable => variable.study != null)
  //          .map(variable => ({ ...variable.study, type: 'study' }));
  //  },
  [getters.FIND_COHORT_SUBJECT_INPUT_VARIABLES]: state =>
    !state.cohort.input_variables
      ? []
      : state.cohort.input_variables
          .filter(variable => variable.subject_ontology != null)
          .map(variable => ({ ...variable.subject_ontology, type: 'subject' })),
  [getters.FIND_COHORT_OBSERVATION_INPUT_VARIABLES]: state => {
    // return !state.cohort.input_variables
    //   ? []
    //   : state.cohort.input_variables
    //       .filter(variable => variable.observation_ontology != null)
    //       .map(variable => ({
    //         ...variable.observation_ontology,
    //         type: 'observation',
    //       }));
    const inputVariables = !state.cohort.input_variables
      ? []
      : state.cohort.input_variables
          .filter(variable => variable.observation_ontology != null)
          .map(variable => {
            let dimLabel = 'value';
            let dimension = '';
            let label = '';

            if ('dimension_label' in variable) {
              dimLabel = variable.dimension_label;
            }

            if (dimLabel === 'left_y_axis') {
              dimension = 'firstVisit';
              label = 'First Visit';
            } else if (dimLabel === 'right_y_axis') {
              dimension = 'lastVisit';
              label = 'Last Visit';
            } else if (dimLabel === 'roc') {
              dimension = 'roc';
              label = 'Rate of Change';
            } else if (dimLabel === 'change') {
              dimension = 'change';
              label = 'Change';
            } else if (dimLabel === 'value') {
              dimension = '';
              label = variable.observation_ontology.label;
            }

            let var_id =
              dimension === ''
                ? variable.observation_ontology_id
                : `${dimension}-${variable.observation_ontology_id}`;

            return {
              parentID: variable.observation_ontology_id,
              parentLabel: variable.observation_ontology.label,
              ...variable.observation_ontology,
              id: var_id,
              label,
              is_longitudinal: variable.is_longitudinal,
              type: 'observation',
            };
          });
    return inputVariables;
  },
  [getters.FIND_COHORT_OBSERVATION_OUTPUT_VARIABLES]: state => {
    const outputVariables = !state.cohort.output_variables
      ? []
      : state.cohort.output_variables
          .filter(variable => variable.observation_ontology != null)
          .map(variable => {
            let dimLabel = 'value';
            let dimension = '';
            let label = '';

            if ('dimension_label' in variable) {
              dimLabel = variable.dimension_label;
            }

            if (dimLabel === 'left_y_axis') {
              dimension = 'firstVisit';
              label = 'First Visit';
            } else if (dimLabel === 'right_y_axis') {
              dimension = 'lastVisit';
              label = 'Last Visit';
            } else if (dimLabel === 'roc') {
              dimension = 'roc';
              label = 'Rate of Change';
            } else if (dimLabel === 'change') {
              dimension = 'change';
              label = 'Change';
            } else if (dimLabel === 'value') {
              dimension = '';
              label = variable.observation_ontology.label;
            }

            let var_id =
              dimension === ''
                ? variable.observation_ontology_id
                : `${dimension}-${variable.observation_ontology_id}`;

            let obs_var = {
              ...variable.observation_ontology,
              id: var_id,
              label,
              is_longitudinal: variable.is_longitudinal,
              type: 'observation',
            };

            obs_var['parentID'] = variable.observation_ontology_id;
            obs_var['parentLabel'] = variable.observation_ontology.label;

            return obs_var;
          });

    // index output vars
    var ovars = {};
    if (state.cohort.output_variables) {
      state.cohort.output_variables.map(v => {
        ovars[v.observation_ontology_id] = v;
      });
    }

    const outcomeMeasures = nest()
      .key(d => d.parentID)
      .entries(outputVariables)
      .filter(d => {
        if (d.key == null || d.key == 'undefined') {
          return true;
        }
        var v = ovars[Number(d.key)];
        var nc = v.observation_ontology.data_category == 'Categorical' ? 2 : 4;
        return d.values.length === nc;
      })
      .map(d => {
        var v = ovars[Number(d.key)];
        return {
          ...v.observation_ontology,
          children: d.values,
        };
      });

    // If a user selected a study with all of its dimensions,
    // we want add just the one study and remove dimensions
    // so we can draw a parallel coordinates plot
    const parentIDs = outcomeMeasures.map(m => m.id);
    const dimensionsNotInParentIDs = outputVariables.filter(
      obs => !parentIDs.includes(obs.parentID)
    );

    return [...outcomeMeasures, ...dimensionsNotInParentIDs];
  },
  [getters.GET_QUERY]: state => dimensionName => {
    const queries = state[stateTypes.QUERIES];
    if (dimensionName in queries) {
      return queries[dimensionName];
    } else {
      return null;
    }
  },
};
