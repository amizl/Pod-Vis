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
    '1-brewer5': { color: '#EFF3FF', class: 'pval-lt-1-brewer5' },
    '0.1-brewer5': { color: '#BDD7E7', class: 'pval-lt-0p1-brewer5' },
    '0.01-brewer5': { color: '#6BAED6', class: 'pval-lt-0p01-brewer5' },
    '0.05-brewer5': { color: '#3182BD', class: 'pval-lt-0p05-brewer5' },
    '0.001-brewer5': { color: '#08519C', class: 'pval-lt-0p001-brewer5' },

    // Brewer 6 class single hue sequential (blue)
    '1-brewer6': { color: '#EFF3FF', class: 'pval-lt-1-brewer6' },
    '0.1-brewer6': { color: '#C6DBEF', class: 'pval-lt-0p1-brewer6' },
    '0.01-brewer6': { color: '#9ECAE1', class: 'pval-lt-0p01-brewer6' },
    '0.05-brewer6': { color: '#6BAED6', class: 'pval-lt-0p05-brewer6' },
    '0.001-brewer6': { color: '#3182BD', class: 'pval-lt-0p001-brewer6' },

    // Brewer 6 class single hue sequential (red)
    '1-brewer6r': { color: '#FEE5D9', class: 'pval-lt-1-brewer6r' },
    '0.1-brewer6r': { color: '#FCBBA1', class: 'pval-lt-0p1-brewer6r' },
    '0.01-brewer6r': { color: '#FC9272', class: 'pval-lt-0p01-brewer6r' },
    '0.05-brewer6r': { color: '#FB6A4A', class: 'pval-lt-0p05-brewer6r' },
    '0.001-brewer6r': { color: '#DE2D26', class: 'pval-lt-0p001-brewer6r' },

    // Blues based off 3f51b5 (Vue primary)
    //    '1': { color: '#9DA1B5', class: 'pval-lt-1' }, // sat = 13
    //    '0.1': { color: '#8F95B5', class: 'pval-lt-0p1' }, // sat = 21
    //    '0.01': { color: '#8189B5', class: 'pval-lt-0p01' }, // sat = 29
    //    '0.001': { color: '#727CB5', class: 'pval-lt-0p001' }, // sat = 37
    //    '0.0001': { color: '#6470B5', class: 'pval-lt-0p0001' }, // sat = 45

    // Trying again with the value cranked up to 100
    '1-val100': { color: '#BFC9FF', class: 'pval-lt-1-val100' }, // sat = 25
    '0.1-val100': { color: '#A6B3FF', class: 'pval-lt-0p1-val100' }, // sat = 35
    '0.01-val100': { color: '#8C9EFF', class: 'pval-lt-0p01-val100' }, // sat = 45
    '0.05-val100': { color: '#7388FF', class: 'pval-lt-0p05-val100' }, // sat = 55
    '0.001-val100': { color: '#5963FF', class: 'pval-lt-0p001-val100' }, // sat = 65

    // Trying again with the value at 80
    '1-val80': { color: '#A3AACF', class: 'pval-lt-1-val80' }, // sat = 21
    '0.1-val80': { color: '#8C97CF', class: 'pval-lt-0p1-val80' }, // sat = 32
    '0.01-val80': { color: '#7683CF', class: 'pval-lt-0p01-val80' }, // sat = 43
    '0.05-val80': { color: '#5F70CF', class: 'pval-lt-0p05-val80' }, // sat = 54
    '0.001-val80': { color: '#485CCF', class: 'pval-lt-0p001-val80' }, // sat = 65
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
