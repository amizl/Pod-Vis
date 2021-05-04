// original - blue, yellow, green
/*
export const colors = {
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
export const colors = {
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
export const colors = {
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
export const colors = {
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
    '1-brewer5': { color: '#FFFFFF', class: 'pval-lt-1-brewer5' },
    '0.1-brewer5': { color: '#BDD7E7', class: 'pval-lt-0p1-brewer5' },
    '0.05-brewer5': { color: '#6BAED6', class: 'pval-lt-0p05-brewer5' },
    '0.01-brewer5': { color: '#3182BD', class: 'pval-lt-0p01-brewer5' },
    '0.001-brewer5': { color: '#08519C', class: 'pval-lt-0p001-brewer5' },

    '1-brewer5v2': { color: '#FFFFFF', class: 'pval-lt-1-brewer5v2' },
    '0.1-brewer5v2': { color: '#EFF3FF', class: 'pval-lt-0p1-brewer5v2' },
    '0.05-brewer5v2': { color: '#BDD7E7', class: 'pval-lt-0p05-brewer5v2' },
    '0.01-brewer5v2': { color: '#6BAED6', class: 'pval-lt-0p01-brewer5v2' },
    '0.001-brewer5v2': { color: '#3182BD', class: 'pval-lt-0p001-brewer5v2' },

    // Brewer 6 class single hue sequential (blue)
    '1-brewer6': { color: '#FFFFFF', class: 'pval-lt-1-brewer6' },
    '0.1-brewer6': { color: '#C6DBEF', class: 'pval-lt-0p1-brewer6' },
    '0.05-brewer6': { color: '#9ECAE1', class: 'pval-lt-0p05-brewer6' },
    '0.01-brewer6': { color: '#6BAED6', class: 'pval-lt-0p01-brewer6' },
    '0.001-brewer6': { color: '#3182BD', class: 'pval-lt-0p001-brewer6' },

    // Brewer 6 class single hue sequential (red)
    '1-brewer6r': { color: '#FFFFFF', class: 'pval-lt-1-brewer6r' },
    '0.1-brewer6r': { color: '#FCBBA1', class: 'pval-lt-0p1-brewer6r' },
    '0.05-brewer6r': { color: '#FC9272', class: 'pval-lt-0p05-brewer6r' },
    '0.01-brewer6r': { color: '#FB6A4A', class: 'pval-lt-0p01-brewer6r' },
    '0.001-brewer6r': { color: '#DE2D26', class: 'pval-lt-0p001-brewer6r' },

    // Brewer 4 class single hue sequential (purple)
    '1-brewer4p': { color: '#FFFFFF', class: 'pval-lt-1-brewer4p' },
    '0.1-brewer4p': { color: '#F2F0F7', class: 'pval-lt-0p1-brewer4p' },
    '0.05-brewer4p': { color: '#CBC9E2', class: 'pval-lt-0p05-brewer4p' },
    '0.01-brewer4p': { color: '#9E9AC8', class: 'pval-lt-0p01-brewer4p' },
    '0.001-brewer4p': { color: '#6A51A3', class: 'pval-lt-0p001-brewer4p' },

    // Brewer 5 class single hue sequential (purple)
    '1-brewer5p': { color: '#FFFFFF', class: 'pval-lt-1-brewer5p' },
    '0.1-brewer5p': { color: '#F2F0F7', class: 'pval-lt-0p1-brewer5p' },
    '0.05-brewer5p': { color: '#CBC9E2', class: 'pval-lt-0p05-brewer5p' },
    '0.01-brewer5p': { color: '#9E9AC8', class: 'pval-lt-0p01-brewer5p' },
    '0.001-brewer5p': { color: '#756BB1', class: 'pval-lt-0p001-brewer5p' },

    // Blues based off 3f51b5 (Vue primary)
    //    '1': { color: '#FFFFFF', class: 'pval-lt-1' }, // sat = 13
    //    '0.1': { color: '#8F95B5', class: 'pval-lt-0p1' }, // sat = 21
    //    '0.01': { color: '#8189B5', class: 'pval-lt-0p01' }, // sat = 29
    //    '0.001': { color: '#727CB5', class: 'pval-lt-0p001' }, // sat = 37
    //    '0.0001': { color: '#6470B5', class: 'pval-lt-0p0001' }, // sat = 45

    // Trying again with the value cranked up to 100
    '1-val100': { color: '#FFFFFF', class: 'pval-lt-1-val100' }, // sat = 25
    '0.1-val100': { color: '#A6B3FF', class: 'pval-lt-0p1-val100' }, // sat = 35
    '0.05-val100': { color: '#8C9EFF', class: 'pval-lt-0p05-val100' }, // sat = 45
    '0.01-val100': { color: '#7388FF', class: 'pval-lt-0p01-val100' }, // sat = 55
    '0.001-val100': { color: '#5963FF', class: 'pval-lt-0p001-val100' }, // sat = 65

    // Trying again with the value at 80
    '1-val80': { color: '#FFFFFF', class: 'pval-lt-1-val80' }, // sat = 21
    '0.1-val80': { color: '#8C97CF', class: 'pval-lt-0p1-val80' }, // sat = 32
    '0.05-val80': { color: '#7683CF', class: 'pval-lt-0p05-val80' }, // sat = 43
    '0.01-val80': { color: '#5F70CF', class: 'pval-lt-0p01-val80' }, // sat = 54
    '0.001-val80': { color: '#485CCF', class: 'pval-lt-0p001-val80' }, // sat = 65
  },

  // Brewer 9 class qualitative - darker colors
  cohorts: [
    '#e41a1c',
    '#cab2d6', // substituted for blue / #377eb8
    '#4daf4a',
    '#984ea3',
    '#ff7f00',
    '#33ff33',
    '#a65628',
    '#fdbf6f', // substituted for pink / #f781bf
    '#999999',
  ],

  // Brewer 9 class qualitative - pastel colors with yellow moved to the end
  bar_graphs: [
    '#8dd3c7',
    '#bebada',
    '#fb8072',
    '#80b1d3', // light blue
    '#fdb462',
    '#b3de69',
    '#fccde5', // light pink
    '#d9d9d9',
    '#ffffb3',
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
