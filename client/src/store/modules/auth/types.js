// State
export const state = {
  USER: 'user',
  AUTH_ERROR: 'authError',
  IS_LOADING: 'isLoading',
};

// Getters
export const getters = {
  IS_USER_AUTHENTICATED: 'isUserAuthenticated',
};

// Mutations
export const mutations = {
  SET_USER: 'setUser',
  SET_LOADING: 'setLoading',
  SET_AUTH_ERROR: 'setAuthError',
  CLEAR_AUTH_ERROR: 'clearAuthError',
  CLEAR_USER: 'clearUser',
};

// Actions
export const actions = {
  CREATE_USER_ACCOUNT: 'createUserAccount',
  SIGN_USER_IN: 'signUserIn',
  SIGN_USER_OUT: 'signUserOut',
  GET_USER_FROM_SESSION: 'getUserFromSession',
};
