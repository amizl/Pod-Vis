// State
export const state = {
  IS_LOADING: 'isLoading',
  COLLECTION: 'collection',
  COLLECTION_SUMMARIES: 'collectionSummaries',
  FIRST_VISIT: 'firstVisit',
  LAST_VISIT: 'lastVisit',
  VISIT_VARIABLE: 'visitVariable',
  TIMES_BETWEEN_VISITS: 'timesBetweenVisits',
  NUM_SELECTED_SUBJECTS: 'numSelectedSubjects',
};

// Mutations
export const mutations = {
  SET_COLLECTION: 'setCollection',
  SET_COLLECTION_SUMMARIES: 'setCollectionSummaries',
  SET_LOADING: 'setLoading',
  SET_FIRST_VISIT: 'setFirstVisit',
  SET_LAST_VISIT: 'setLastVisit',
  SET_VISIT_VARIABLE: 'setVisitVariable',
  SET_TIMES_BETWEEN_VISITS: 'setTimesBetweenVisits',
  SET_NUM_SELECTED_SUBJECTS: 'setNumSelectedSubjects',
};

// Actions
export const actions = {
  FETCH_COLLECTION: 'fetchCollection',
  FETCH_COLLECTION_SUMMARIES: 'fetchCollectionSummaries',
  SET_FIRST_VISIT: 'setFirstVisit',
  SET_LAST_VISIT: 'setLastVisit',
  SET_VISIT_VARIABLE: 'setVisitVariable',
  FETCH_TIMES_BETWEEN_VISITS: 'fetchTimesBetweenVisits',
  SAVE_FIRST_AND_LAST_VISITS: 'saveFirstAndLastVisits',
};
