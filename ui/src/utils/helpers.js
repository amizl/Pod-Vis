import { uniqBy } from "lodash";
import crossfilter from "crossfilter2";

export function makeHierarchy(data) {
  const ontologies = data.map(obs => obs.ontology);
  ontologies.forEach(o => {
    if (!o.parent) {
      o.parent = null;
    }
  });

  const parents = uniqBy(
    ontologies.map(ontology => (ontology.parent ? ontology.parent : ontology)),
    "label"
  );

  return parents.map(parent => ({
    ...parent,
    children: ontologies.filter(
      ontology => ontology.parent && ontology.parent.label === parent.label
    )
  }));
}

export function getInputVariablesFromQueries(queries, inputVariables) {
  var inputVars = [];

  Object.keys(queries).forEach(variable => {
    var query = queries[variable];
    var iv = inputVariables.find(inputVar => {
      const { label, type } = inputVar;
      if (type === "study" || type === "subject") {
        return label === variable;
      }
      // type is 'observation'
      const { parentLabel, is_longitudinal } = inputVar;
      const obsLabel =
        parentLabel && is_longitudinal ? `${parentLabel} - ${label}` : label;
      return obsLabel === variable;
    });
    if (iv) {
      inputVars.push({ query: query, variable: iv });
    }
  });

  return inputVars;
}

export function getCohortSubjectIds(data, c) {
  // determine which subjects are in the cohort
  const xf = crossfilter(data);

  const dimension2field = {
    left_y_axis: "firstVisit",
    right_y_axis: "lastVisit",
    change: "change",
    roc: "roc",
    value: "value"
  };

  // group queries by variable - categorical vars must be treated differently
  var var2qs = {};
  c.queries.forEach(q => {
    let v_id;
    let accessor;
    let dim;
    let dim_label = "value";

    if (q.input_variable.subject_ontology === undefined) {
      v_id = q.input_variable.observation_ontology.id;
      if (
        "dimension_label" in q.input_variable &&
        q.input_variable.dimension_label != ""
      ) {
        dim_label = q.input_variable.dimension_label;
      }
      const subfield = dimension2field[dim_label];
      accessor = function(d) {
        return d[q.input_variable.observation_ontology.id][subfield];
      };
      dim = xf.dimension(accessor);
    } else {
      v_id = q.input_variable.subject_ontology.id;
      const lbl = q.input_variable.subject_ontology.label;
      // special case for study/dataset
      if (lbl === "Study" || lbl === "Dataset") {
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

    var vkey = v_id;
    if (dim_label != null) {
      vkey += ":" + dim_label;
    }
    if (!(vkey in var2qs)) {
      var2qs[vkey] = { accessor: accessor, dim: dim, queries: [] };
    }
    var2qs[vkey]["queries"].push(q);
  });

  Object.keys(var2qs).forEach(k => {
    var v = var2qs[k];
    var filterFn = null;
    var nq = v["queries"].length;
    if (nq == 0) throw new Error("No queries for variable " + k);

    // currently only categorical variables should have multiple queries
    if (nq > 1) {
      filterFn = function(d) {
        var any_matches = false;
        v["queries"].forEach(q => {
          if (d === q.value) {
            any_matches = true;
          }
        });
        return any_matches;
      };
    } else {
      var q = v["queries"][0];
      if (q.value !== undefined && q.value !== null) {
        filterFn = function(d) {
          return d === q.value;
        };
      } else if (q.min_value !== undefined && q.max_value !== undefined) {
        filterFn = function(d) {
          var dv = d * 1.0;
          return dv >= q.min_value && dv < q.max_value;
        };
      } else {
        throw new Error(`Unsupported query ${q}`);
      }
    }
    v["dim"].filterFunction(filterFn);
  });

  const filt = xf.allFiltered();
  const sids = {};
  filt.forEach(r => {
    sids[r.subject_id] = 1;
  });

  const cohortSubjectIds = Object.keys(sids);
  return cohortSubjectIds;
}

export function getObservationVariableAbbreviations(c) {
  var collectionVarAbbreviations = {};
  var getCollectionVarAbbreviations = function(vars) {
    vars.forEach(v => {
      if (v.children && v.children.length > 0) {
        if (v.children[0].label === "First Visit") {
          collectionVarAbbreviations[v.abbreviation] = true;
        } else {
          getCollectionVarAbbreviations(v.children);
        }
      }
    });
  };

  getCollectionVarAbbreviations(c.observation_variables);
  return collectionVarAbbreviations;
}

export function getObservationVariableAbbreviationToName(c) {
  var collectionVarAbbreviations = {};
  var getCollectionVarAbbreviations = function(vars) {
    vars.forEach(v => {
      if (v.children && v.children.length > 0) {
        if (v.children[0].label === "First Visit") {
          collectionVarAbbreviations[v.abbreviation] = v.label;
        } else {
          getCollectionVarAbbreviations(v.children);
        }
      }
    });
  };

  getCollectionVarAbbreviations(c.observation_variables);
  return collectionVarAbbreviations;
}

export function getObservationVariableAbbreviationToDescription(c) {
  var collectionVarAbbreviations = {};
  var getCollectionVarAbbreviations = function(vars) {
    vars.forEach(v => {
      if (v.children && v.children.length > 0) {
        if (v.children[0].label === "First Visit") {
          collectionVarAbbreviations[v.abbreviation] = v.description;
        } else {
          getCollectionVarAbbreviations(v.children);
        }
      }
    });
  };

  getCollectionVarAbbreviations(c.observation_variables);
  return collectionVarAbbreviations;
}

export function getObservationVariableNames(c) {
  var collectionVarNames = {};
  var getCollectionVarNames = function(vars) {
    vars.forEach(v => {
      if (v.children && v.children.length > 0) {
        if (v.children[0].label === "First Visit") {
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
        if (v.children[0].label === "First Visit") {
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
    if (ov[which + "_visit_event"] != null) {
      evt = ov[which + "_visit_event"];
    } else if (ov[which + "_visit_num"] != null) {
      evt = ov[which + "_visit_num"];
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
  descr += ": ";
  var nc = null;

  if (c.num_cohorts) {
    nc = c.num_cohorts;
    descr += " " + nc + (nc == 1 ? "cohort." : " cohorts.");
  } else if (c.cohorts) {
    nc = c.cohorts.length;
    descr += " " + nc + (nc == 1 ? "cohort." : " cohorts.");
  }

  descr += " " + (nsv + nov) + " variables ";

  var nd = c.studies.length;
  descr +=
    "from " + nd + " uploaded " + (nd == 1 ? "dataset" : "datasets") + " [";
  descr += c.studies.map(s => s.study.study_name).join(",");
  descr += "]";

  if (c.has_visits_set) {
    var fvs = getCollectionVisitCounts(c, "first");
    var lvs = getCollectionVisitCounts(c, "last");
    descr +=
      " First Visits: " + fvs.map(v => v.visit + "[" + v.count + "]").join(",");
    descr +=
      " Last Visits: " + lvs.map(v => v.visit + "[" + v.count + "]").join(",");
  }

  return descr;
}

// PPMI-specific workaround
export function sortByVisitEvent(unsorted_list, event_accessor_fn) {
  var numericEvents = true;
  var pseudoNumericEvents = true;
  var pnRE = /^[A-Z]+(-?[\d.]+)$/i;

  unsorted_list.forEach(e => {
    var evt = event_accessor_fn(e);
    if (typeof evt == "string" && !evt.match(pnRE)) {
      pseudoNumericEvents = false;
    }
    if (isNaN(evt)) {
      numericEvents = false;
    }
  });

  // sort numerically
  if (numericEvents) {
    return unsorted_list.sort(
      (a, b) => event_accessor_fn(a) - event_accessor_fn(b)
    );
  }
  // sort numerically, ignorning non-numeric component
  if (pseudoNumericEvents) {
    var pnAccFn = a => {
      var evt = event_accessor_fn(a);
      var m = evt.match(pnRE)[1];
      return m;
    };

    return unsorted_list.sort((a, b) => pnAccFn(a) - pnAccFn(b));
  }

  // sort alphabetically but put PPMI and EMA events in the correct order
  var uniqueEvents = [
    "Pre",
    "3 mo",
    "6 mo",
    "SC",
    "BL",
    "U01",
    "V01",
    "V02",
    "V03",
    "V04",
    "V05",
    "V06",
    "V07",
    "V08",
    "V09",
    "V10",
    "V11",
    "V12",
    "V13",
    "V14",
    "V15",
    "V16",
    "PW",
    "ST"
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

export function scaleSortFn(sort) {
  return function(sa, sb) {
    var a = sa.ontology ? sa.ontology : sa;
    var b = sb.ontology ? sb.ontology : sb;
   
    console.log("***THIS IS SORT ", sort);
    if (sort == "Selection") {
      console.log("***THIS IS SORT BY SELECTION*** ", sort);
      if (a.type == "subject" && b.type == "observation") return 1;
      if (a.type == "observation" && b.type == "subject") return -1;
      if (a.category < b.category) return -1;
      if (a.category > b.category) return 1;
      if (a.label < b.label) return -1;
      if (a.label > b.label) return 1;
      if (a.scale < b.scale) return -1;
      if (a.scale > b.scale) return 1;
      return 0;
    } else {
      if (a.type == "subject" && b.type == "observation") return -1;
      if (a.type == "observation" && b.type == "subject") return 1;
      if (a.category > b.category) return -1;
      if (a.category < b.category) return 1;
      if (a.label < b.label) return -1;
      if (a.label > b.label) return 1;
      if (a.scale < b.scale) return -1;
      if (a.scale > b.scale) return 1;
      return 0;
    }
  };
}

export function sortScales(scales,sort) {
  return scales.sort(scaleSortFn(sort));
}

export function getLongScaleNameDefault(datasets) {
  const long_re = / EMA /;
  var useLong = false;
  datasets.forEach(sd => {
    if (sd.study_name.match(long_re)) {
      useLong = true;
    }
  });
  return useLong;
}

export function getLabelWidth(label) {
  const fm = 17;
  if (label.length <= 3) {
    return label.length * fm * 2.2;
  } else if (label.length <= 6) {
    return label.length * fm * 1.4;
  } else if (label.length >= 15) {
    return label.length * fm * 0.8;
  }
  return label.length * fm;
}

/**
 * Given a list of [variable_id, first_index, last_index], generate a set of subject counts
 * using the data in subject_variable_visits.
 *
 * subject_variable_visits - value returned by /api/studies/subject_variable_visits
 * which - either 'event' or 'num'
 */
export function countSubjectsByVisits(subject_variable_visits, vars, which) {
  var subjCounts = { all: 0 };
  var subjs = subject_variable_visits["subjects"];
  var subjIds = Object.keys(subjs);

  // subjs:
  // "subjects": {
  //   <subj_id>: {
  //    "25": 1,     <- subject_ontology
  //    "26": 1,
  //    "361": {     <- observation_ontology
  //  	"event": "100000000000000000000",
  //           "num": "000000000010000000"
  //            },
  //   }
  // }

  subjIds.forEach(sid => {
    var s = subjs[sid];
    var include_subj = true;
    var study_ids = Object.keys(s);
    study_ids.forEach(study_id => {
      if (!(study_id in subjCounts)) {
        subjCounts[study_id] = 0;
      }
      vars.forEach(v => {
        if (!(v[0] in s[study_id])) {
          include_subj = false;
        } else if (typeof s[study_id][v[0]] != "number") {
          var vstring = s[study_id][v[0]][which];
          if (vstring.charAt(v[1]) == "0" || vstring.charAt(v[2]) == "0") {
            include_subj = false;
          }
        }
      });
    });
    if (vars.length > 0 && include_subj) {
      subjCounts["all"] += 1;
      study_ids.forEach(study_id => {
        subjCounts[study_id] += 1;
      });
    }
  });
  return subjCounts;
}

/**
 * Estimate the maximum number of subjects that could be obtained with the selected
 * set of variables, returning the first and last visit selections that would produce
 * the estimated result.
 *
 * subject_variable_visits - value returned by /api/studies/subject_variable_visits
 * var_ids - list of observation variable ids
 * which - either 'event' or 'num'
 */
export function estimateMaxSubjects(subject_variable_visits, var_ids, which) {
  var subjs = subject_variable_visits["subjects"];
  var subjIds = Object.keys(subjs);
  var visits = subject_variable_visits["visits"][which];
  var n_visits = visits.length;

  // simple heuristic based on selecting the two visits from each variable with the most subjects
  var vars = [];

  var_ids.forEach(vid => {
    // get visit counts for variable vid
    var visitCounts = [];

    subjIds.forEach(sid => {
      var s = subjs[sid];
      var study_ids = Object.keys(s);
      study_ids.forEach(study_id => {
        if (vid in s[study_id] && typeof s[study_id][vid] != "number") {
          var vstring = s[study_id][vid][which];
          for (var vis = 0; vis < n_visits; ++vis) {
            if (!(vis in visitCounts))
              visitCounts[vis] = { index: vis, count: 0 };
            if (vstring.charAt(vis) == "1") {
              visitCounts[vis]["count"] += 1;
            }
          }
        }
      });
    });

    // heuristic - sort by size and pick the top two, then sort by index
    visitCounts.sort((a, b) => b["count"] - a["count"]);
    var first_index = 0;
    var last_index = 0;

    if (visitCounts.length > 1) {
      if (visitCounts[0]["index"] < visitCounts[1]["index"]) {
        first_index = visitCounts[0]["index"];
        last_index = visitCounts[1]["index"];
      } else {
        first_index = visitCounts[1]["index"];
        last_index = visitCounts[0]["index"];
      }
    }
    vars.push([vid, first_index, last_index]);
  });
  var counts = countSubjectsByVisits(subject_variable_visits, vars, which);
  return { counts: counts, visits: vars };
}

/**
 * Variant of estimateMaxSubjects that tries to maximize the time between first
 * and last visit.
 *
 * subject_variable_visits - value returned by /api/studies/subject_variable_visits
 * var_ids - list of observation variable ids
 * which - either 'event' or 'num'
 * min_subjects - minimum number of subjects to return
 */
export function estimateMaxVisits(
  subject_variable_visits,
  var_ids,
  which,
  min_subjects
) {
  var subjs = subject_variable_visits["subjects"];
  var subjIds = Object.keys(subjs);
  var visits = subject_variable_visits["visits"][which];
  var n_visits = visits.length;

  var vars = [];

  var_ids.forEach(vid => {
    // get visit counts for variable vid
    var visitCounts = [];

    subjIds.forEach(sid => {
      var s = subjs[sid];
      var study_ids = Object.keys(s);
      study_ids.forEach(study_id => {
        if (vid in s[study_id] && typeof s[study_id][vid] != "number") {
          var vstring = s[study_id][vid][which];
          for (var vis = 0; vis < n_visits; ++vis) {
            if (!(vis in visitCounts))
              visitCounts[vis] = { index: vis, count: 0 };
            if (vstring.charAt(vis) == "1") {
              visitCounts[vis]["count"] += 1;
            }
          }
        }
      });
    });

    visitCounts.sort((a, b) => b["count"] - a["count"]);
    var first_index = 0;
    var last_index = 0;

    // make the first visit the one with the most subjects
    if (visitCounts.length > 1) {
      if (visitCounts[0]["index"] < visitCounts[1]["index"]) {
        first_index = visitCounts[0]["index"];
      } else {
        first_index = visitCounts[1]["index"];
      }
      last_index = n_visits - 1;
    }
    vars.push([vid, first_index, last_index]);
  });

  // move last index backwards until we exceed the desired threshold or
  // hit the first index in at least one variable
  let done = false;
  var counts = null;

  while (!done) {
    counts = countSubjectsByVisits(subject_variable_visits, vars, which);
    // halt if desired threshold exceeded
    if (counts["all"] >= min_subjects) {
      done = true;
      break;
    }

    let last_index = vars[0][2];
    let new_vars = [];
    vars.forEach(v => {
      let nv = [v[0], v[1], last_index - 1];
      new_vars.push(nv);

      // halt when first + last coincide
      if (nv[2] == nv[1]) {
        done = true;
      }
    });
    if (!done) vars = new_vars;
  }
  counts = countSubjectsByVisits(subject_variable_visits, vars, which);
  return { counts: counts, visits: vars };
}
