// State
export const state = {
  IS_LOADING: 'isLoading',
  COLLECTION: 'collection',
  COLLECTION_SUMMARIES: 'collectionSummaries',
  FIRST_VISIT: 'firstVisit',
  LAST_VISIT: 'lastVisit',
  VISIT_VARIABLE: 'visitVariable',
};

// Mutations
export const mutations = {
  SET_COLLECTION: 'setCollection',
  SET_COLLECTION_SUMMARIES: 'setCollectionSummaries',
  SET_LOADING: 'setLoading',
  SET_FIRST_VISIT: 'setFirstVisit',
  SET_LAST_VISIT: 'setLastVisit',
  SET_VISIT_VARIABLE: 'setVisitVariable',
};

// Actions
export const actions = {
  FETCH_COLLECTION: 'fetchCollection',
  FETCH_COLLECTION_SUMMARIES: 'fetchCollectionSummaries',
  SET_FIRST_VISIT: 'setFirstVisit',
  SET_LAST_VISIT: 'setLastVisit',
  SET_VISIT_VARIABLE: 'setVisitVariable',
};
