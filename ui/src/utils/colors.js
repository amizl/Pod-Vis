// original - blue, yellow, green
/*
export let colors = {
  population: '#F8D580',
  'cohort-circle-fill': 'blue',
  'cohort-circle-fill-opacity': '0.8',
  'cohort-circle-stroke': '#2bdb60',
  'cohort-circle-stroke-width': '2',

  cohort: '#3F51B5',
  'population-circle-fill': '#F88123',
  'population-circle-fill-opacity': '0.8',
  'population-circle-stroke': '#f8d537',
  'population-circle-stroke-width': '2',

  nonCohort: '#3FB551',
};
*/
// silver/grey
/*
export let colors = {
  'population': '#D1D3D4',
  'cohort-circle-fill': 'blue',
  'cohort-circle-fill-opacity': '0.8',
  'cohort-circle-stroke': '#2bdb60',
  'cohort-circle-stroke-width': '2',
  'cohort': '#3F51B5',
  'population-circle-fill': "#F88123",
  'population-circle-fill-opacity': '0.8',
  'population-circle-stroke': "#f8d537",
  'population-circle-stroke-width': '2',
  'nonCohort': '#3FB551',
};
*/

// silver/grey/"light blue"
/*
export let colors = {
  'population': '#8C99A5',
  'cohort-circle-fill': 'blue',
  'cohort-circle-fill-opacity': '0.8',
  'cohort-circle-stroke': '#2bdb60',
  'cohort-circle-stroke-width': '2',
  'cohort': '#3F51B5',
  'population-circle-fill': "#F88123",
  'population-circle-fill-opacity': '0.8',
  'population-circle-stroke': "#f8d537",
  'population-circle-stroke-width': '2',
  'nonCohort': '#3FB551',
};
*/
// grey/light blue
export let colors = {
  cohort: '#3F51B5',
  'cohort-circle-fill': '#1B33B5',
  'cohort-circle-fill-opacity': '0.8',
  'cohort-circle-stroke': '#769eb5',
  'cohort-circle-stroke-width': '2',

  population: '#B8D6FF',
  'population-circle-fill': '#85B9FF',
  'population-circle-fill-opacity': '0.8',
  'population-circle-stroke': '#E1FFE1',
  'population-circle-stroke-width': '2',

  nonCohort: '#3FB551',

  'warn-background': '#F83008',
  'warn-text': '#F8D5F0',

  firstVisit: '#8bdb35',
  'firstVisit-opacity': '0.4',
  lastVisit: '#db5454',
  'lastVisit-opacity': '0.4',
};

export function getNumSubjectsColor(nSubjects) {
  if (nSubjects <= 25) {
    return colors['warn-background'];
  } else {
    return colors['population'];
  }
}

export function getNumSubjectsTextColor(nSubjects) {
  if (nSubjects <= 25) {
    return colors['warn-text'];
  } else {
    return '#273CDC';
  }
}
