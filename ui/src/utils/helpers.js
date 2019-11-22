import { uniqBy } from 'lodash';
import * as crossfilter from 'crossfilter2';

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
  return Object.keys(queries).map(variable => {
    return {
      query: queries[variable],
      variable: inputVariables.find(inputVar => {
        const { label, type } = inputVar;
        if (type === 'study' || type === 'subject') {
          return label === variable;
        } else {
          // type is 'observation'
          const { parentLabel } = inputVar;
          const obsLabel = `${parentLabel} - ${label}`;
          return obsLabel === variable;
        }
      }),
    };
  });
}

export function getCohortSubjectIds(data, c) {
    // determine which subjects are in the cohort
    const xf = crossfilter(data);

    c.queries.forEach(function(q) {
        // adapted from FIND_COHORT_QUERY
        const inputVariable = q.input_variable;
        var filter_fn = undefined;
        let accessor = undefined;
        let dim = undefined;
	
        if (q.input_variable.subject_ontology === undefined) {
            // convert dimension_label to data field name
            let subfield = dimension2field[q.input_variable.dimension_label];
            accessor = function(d) { return d[q.input_variable.observation_ontology.id][subfield] };
            dim = xf.dimension(accessor);
        } else {
            let lbl = q.input_variable.subject_ontology.label;
            // special case for study
            if (lbl === "Study") {
		accessor = function(d) { return d["study"]["study_name"] };
            } else {
		accessor = function(d) { return d[lbl] };
            }
            dim = xf.dimension(accessor);
        }
	
        if ((q.value !== undefined) && (q.value !== null)) {
            filter_fn = function(d) { return d === q.value; };
            dim.filterFunction(filter_fn);
        } else if ((q.min_value !== undefined) && (q.max_value !== undefined)) {
            filter_fn = function(d) { return ((d >= q.min_value) && (d <= q.max_value)); };
            dim.filterFunction(filter_fn);
        } else {
            console.log("unsupported query " + q);
        }
    });
    const filt = xf.allFiltered();
    
    let sids = {};
    filt.forEach(function(r) {
        sids[r.subject_id] = 1;
    });
    
    var cohort_subject_ids = Object.keys(sids);
    return cohort_subject_ids;
}
