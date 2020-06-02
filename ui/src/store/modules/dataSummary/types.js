// State
export const state = {
  IS_LOADING: 'isLoading',
  COLLECTION: 'collection',
  COLLECTION_SUMMARY: 'collectionSummary',
  FIRST_VISIT: 'firstVisit',
  LAST_VSIST: 'lastVisit',
  VISIT_VARIABLE: 'visitVariable',
};

// Mutations
export const mutations = {
  SET_COLLECTION: 'setCollection',
  SET_COLLECTION_SUMMARY: 'setCollectionSummary',
  SET_LOADING: 'setLoading',
  SET_FIRST_VISIT: 'setFirstVisit',
  SET_LAST_VISIT: 'setLastVisit',
};

// Actions
export const actions = {
  FETCH_COLLECTION: 'fetchCollection',
  FETCH_COLLECTION_SUMMARY_BY_EVENT: 'fetchCollectionSummaryByEvent',
  SET_FIRST_VISIT: 'setFirstVisit',
  SET_LAST_VISIT: 'setLastVisit',
};
