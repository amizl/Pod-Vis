import { uniqBy } from 'lodash';
import crossfilter from 'crossfilter2';

export function makeHierarchy(data) {
  const ontologies = data.map(obs => obs.ontology);
  const parents = uniqBy(
    ontologies.map(ontology => ontology.parent),
    'label'
  ).map(parent => ({
    ...parent,
    children: ontologies.filter(
      ontology => ontology.parent.label === parent.label
    ),
  }));
  return parents;
}

export function getInputVariablesFromQueries(queries, inputVariables) {
  return Object.keys(queries).map(variable => ({
    query: queries[variable],
    variable: inputVariables.find(inputVar => {
      const { label, type } = inputVar;
      if (type === 'study' || type === 'subject') {
        return label === variable;
      }
      // type is 'observation'
      const { parentLabel } = inputVar;
      const obsLabel = `${parentLabel} - ${label}`;
      return obsLabel === variable;
    }),
  }));
}

export function getCohortSubjectIds(data, c) {
  // determine which subjects are in the cohort
  const xf = crossfilter(data);

  const dimension2field = {
    left_y_axis: 'firstVisit',
    right_y_axis: 'lastVisit',
    change: 'change',
    roc: 'roc',
  };

  c.queries.forEach(q => {
    // adapted from FIND_COHORT_QUERY
    let filterFn;
    let accessor;
    let dim;

    if (q.input_variable.subject_ontology === undefined) {
      // convert dimension_label to data field name
      const subfield = dimension2field[q.input_variable.dimension_label];
      accessor = function(d) {
        return d[q.input_variable.observation_ontology.id][subfield];
      };
      dim = xf.dimension(accessor);
    } else {
      const lbl = q.input_variable.subject_ontology.label;
      // special case for study
      if (lbl === 'Study') {
        accessor = function(d) {
          return d.study.study_name;
        };
      } else {
        accessor = function(d) {
          return d[lbl];
        };
      }
      dim = xf.dimension(accessor);
    }

    if (q.value !== undefined && q.value !== null) {
      filterFn = function(d) {
        return d === q.value;
      };
      dim.filterFunction(filterFn);
    } else if (q.min_value !== undefined && q.max_value !== undefined) {
      filterFn = function(d) {
        return d >= q.min_value && d <= q.max_value;
      };
      dim.filterFunction(filterFn);
    } else {
      throw new Error(`Unsupported query ${q}`);
    }
  });
  const filt = xf.allFiltered();

  const sids = {};
  filt.forEach(r => {
    sids[r.subject_id] = 1;
  });

  const cohortSubjectIds = Object.keys(sids);
  return cohortSubjectIds;
}
