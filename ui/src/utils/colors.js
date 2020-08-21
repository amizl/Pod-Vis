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
    //    '1': { color: '#FEEDDE', class: 'pval-lt-1' },
    //    '0.1': { color: '#FDD0A2', class: 'pval-lt-0p1' },
    //    '0.01': { color: '#FDAE6B', class: 'pval-lt-0p01' },
    //    '0.001': { color: '#FD8D3C', class: 'pval-lt-0p001' },
    //    '0.0001': { color: '#F16913', class: 'pval-lt-0p0001' },

    // Brewer 5 class single hue sequential (blue)
//    '1': { color: '#EFF3FF', class: 'pval-lt-1' },
//    '0.1': { color: '#BDD7E7', class: 'pval-lt-0p1' },
//    '0.01': { color: '#6BAED6', class: 'pval-lt-0p01' },
//    '0.001': { color: '#3182BD', class: 'pval-lt-0p001' },
//    '0.0001': { color: '#08519C', class: 'pval-lt-0p0001' },

    // Blues based off 3f51b5 (Vue primary)
//    '1': { color: '#9DA1B5', class: 'pval-lt-1' }, // sat = 13
//    '0.1': { color: '#8F95B5', class: 'pval-lt-0p1' }, // sat = 21
//    '0.01': { color: '#8189B5', class: 'pval-lt-0p01' }, // sat = 29
//    '0.001': { color: '#727CB5', class: 'pval-lt-0p001' }, // sat = 37
//    '0.0001': { color: '#6470B5', class: 'pval-lt-0p0001' }, // sat = 45

    // Trying again with the value cranked up to 100
    '1': { color: '#BFC9FF', class: 'pval-lt-1' }, // sat = 25
    '0.1': { color: '#A6B3FF', class: 'pval-lt-0p1' }, // sat = 35
    '0.01': { color: '#8C9EFF', class: 'pval-lt-0p01' }, // sat = 45
    '0.001': { color: '#7388FF', class: 'pval-lt-0p001' }, // sat = 55
    '0.0001': { color: '#5973FF', class: 'pval-lt-0p0001' }, // sat = 65

    // Trying again with the value at 81
//    '1': { color: '#A3AACF', class: 'pval-lt-1' }, // sat = 21
//    '0.1': { color: '#8C97CF', class: 'pval-lt-0p1' }, // sat = 32
//    '0.01': { color: '#7683CF', class: 'pval-lt-0p01' }, // sat = 43
//    '0.001': { color: '#5F70CF', class: 'pval-lt-0p001' }, // sat = 54
//    '0.0001': { color: '#485CCF', class: 'pval-lt-0p0001' }, // sat = 65

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
