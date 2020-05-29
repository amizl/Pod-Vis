import { uniqBy } from 'lodash';
import crossfilter from 'crossfilter2';

export function makeHierarchy(data) {
  const ontologies = data.map(obs => obs.ontology);
  ontologies.forEach(o => {
    if (!o.parent) {
      o.parent = null;
    }
  });

  const parents = uniqBy(
    ontologies.map(ontology => (ontology.parent ? ontology.parent : ontology)),
    'label'
  );

  return parents.map(parent => ({
    ...parent,
    children: ontologies.filter(
      ontology => ontology.parent && ontology.parent.label === parent.label
    ),
  }));
}

export function getInputVariablesFromQueries(queries, inputVariables) {
  var inputVars = [];

  Object.keys(queries).forEach(variable => {
    var query = queries[variable];
    var variable = inputVariables.find(inputVar => {
      const { label, type } = inputVar;
      if (type === 'study' || type === 'subject') {
        return label === variable;
      }
      // type is 'observation'
      const { parentLabel } = inputVar;
      const obsLabel = `${parentLabel} - ${label}`;
      return obsLabel === variable;
    });
    if (variable) {
      inputVars.push({ query: query, variable: variable });
    }
  });

  return inputVars;
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

export function getObservationVariableNames(c) {
  var collectionVarNames = {};
  var getCollectionVarNames = function(vars) {
    vars.forEach(v => {
      if (v.children && v.children.length > 0) {
        if (v.children[0].label === 'First Visit') {
          collectionVarNames[v.label] = true;
        } else {
          getCollectionVarNames(v.children);
        }
      }
    });
  };

  getCollectionVarNames(c.observation_variables);
  return collectionVarNames;
}

export function getObservationVariableIds(c) {
  var collectionVarIds = {};
  var getCollectionVarIds = function(vars) {
    vars.forEach(v => {
      if (v.children && v.children.length > 0) {
        if (v.children[0].label === 'First Visit') {
          collectionVarIds[v.id] = true;
        } else {
          getCollectionVarIds(v.children);
        }
      }
    });
  };

  getCollectionVarIds(c.observation_variables);
  return Object.keys(collectionVarIds);
}
