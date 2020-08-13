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

  pvals: {
    '1': { color: '#FEEDDE', class: 'pval-lt-1' },
    '0.1': { color: '#FDD0A2', class: 'pval-lt-0p1' },
    '0.01': { color: '#FDAE6B', class: 'pval-lt-0p01' },
    '0.001': { color: '#FD8D3C', class: 'pval-lt-0p001' },
    '0.0001': { color: '#F16913', class: 'pval-lt-0p0001' },
  },

  cohorts: [
      '#e41a1c',
      '#377eb8',
      '#4daf4a',
      '#984ea3',
      '#ff7f00',
      '#ffff33',
      '#a65628',
      '#f781bf',
      '#999999',
  ],

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
