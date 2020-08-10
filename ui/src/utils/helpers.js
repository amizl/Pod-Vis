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

export function getCollectionVisitCounts(c, which) {
  var counts = [];
  var ch = {};
  var obs_vars = c.observation_variables_list
    ? c.observation_variables_list
    : c.observation_variables;

  obs_vars.forEach(ov => {
    var evt = null;
    if (ov[which + '_visit_event'] != null) {
      evt = ov[which + '_visit_event'];
    } else if (ov[which + '_visit_num'] != null) {
      evt = ov[which + '_visit_num'];
    }

    if (!(evt in ch)) {
      ch[evt] = 0;
    }
    ch[evt] += 1;
  });

  // sort by decreasing count
  Object.keys(ch)
    .sort((a, b) => ch[b] - ch[a])
    .forEach(k => {
      counts.push({ visit: k, count: ch[k] });
    });

  return counts;
}

export function getCollectionDescription(c) {
  var descr = c.label;
  var obs_vars = c.observation_variables_list
    ? c.observation_variables_list
    : c.observation_variables;
  var nsv = c.subject_variables.length;
  var nov = obs_vars.length;
  descr += ': ';

  if (c.num_cohorts) {
    var nc = c.num_cohorts;
    descr += ' ' + nc + (nc == 1 ? 'cohort.' : ' cohorts.');
  } else if (c.cohorts) {
    var nc = c.cohorts.length;
    descr += ' ' + nc + (nc == 1 ? 'cohort.' : ' cohorts.');
  }

  descr += ' ' + (nsv + nov) + ' variables ';

  var nd = c.studies.length;
  descr +=
    'from ' + nd + ' uploaded ' + (nd == 1 ? 'dataset' : 'datasets') + ' [';
  descr += c.studies.map(s => s.study.study_name).join(',');
  descr += ']';

  if (c.has_visits_set) {
    var fvs = getCollectionVisitCounts(c, 'first');
    var lvs = getCollectionVisitCounts(c, 'last');
    descr +=
      ' First Visits: ' + fvs.map(v => v.visit + '[' + v.count + ']').join(',');
    descr +=
      ' Last Visits: ' + lvs.map(v => v.visit + '[' + v.count + ']').join(',');
  }

  return descr;
}

// PPMI-specific workaround
export function sortByVisitEvent(unsorted_list, event_accessor_fn) {
  var numericEvents = true;
  unsorted_list.forEach(e => {
    if (isNaN(event_accessor_fn(e))) {
      numericEvents = false;
    }
  });

  // sort numerically
  if (numericEvents) {
    return unsorted_list.sort(
      (a, b) => event_accessor_fn(a) - event_accessor_fn(b)
    );
  }

  var uniqueEvents = [
    'SC',
    'BL',
    'U01',
    'V01',
    'V02',
    'V03',
    'V04',
    'V05',
    'V06',
    'V07',
    'V08',
    'V09',
    'V10',
    'V11',
    'V12',
    'V13',
    'V14',
    'V15',
    'V16',
    'PW',
    'ST',
  ];

  var evtIdx = {};
  var ind = 1;
  uniqueEvents.forEach(e => {
    evtIdx[e] = ind++;
  });
  function getIndex(evt) {
    return evt in evtIdx ? evtIdx[evt] : ind + 1;
  }

  function sortFn(a, b) {
    var a_evt = event_accessor_fn(a);
    var b_evt = event_accessor_fn(b);
    var a_i = getIndex(a_evt);
    var b_i = getIndex(b_evt);
    if (a_i < b_i) return -1;
    if (b_i < a_i) return 1;
    return a_evt.localeCompare(b_evt);
  }

  return unsorted_list.sort(sortFn);
}

export function sortVisitEvents(events) {
  var acc_fn = x => x;
  return sortByVisitEvent(events, acc_fn);
}
