// Getters
export const getters = {
  USER: 'USER',
  ERROR: 'AUTH_ERROR',
  LOADING: 'LOADING',
};

// Mutations
export const mutations = {
  SET_USER: 'SET_USER',
  SET_LOADING: 'SET_LOADING',
  SET_AUTH_ERROR: 'SET_AUTH_ERROR',
  CLEAR_AUTH_ERROR: 'CLEAR_AUTH_ERROR',
  CLEAR_USER: 'CLEAR_USER',
};

// Actions
export const actions = {
  CREATE_USER_ACCOUNT: 'CREATE_USER_ACCOUNT',
  SIGN_USER_IN: 'SIGN_USER_IN',
  SIGN_USER_OUT: 'SIGN_USER_OUT',
  AUTO_SIGN_IN: 'AUTO_SIGN_IN',
};
