/**
 * Authentication Navigation Gaurds.
 *
 * These handle the logic before entering a particular route.
 * There are routes where a user needs to be authenticated (dashboard), and were
 * you can't be authenticated (sign in page).
 */

import store from '@/store';
import {
  actions as authActions,
  getters as authGetters,
} from '@/store/modules/auth/types';

const authModule = 'auth';

/**
 * Lazy evaluated function to determine if user is authenticated.
 */
const isUserAuthenticated = () => {
  const isUserAuthenticated = authGetters.IS_USER_AUTHENTICATED;
  return store.getters[`${authModule}/${isUserAuthenticated}`];
};

export const requireAuth = async (to, from, next) => {
  await store.dispatch(`${authModule}/${authActions.VALIDATE_TOKEN}`);
  if (!isUserAuthenticated()) next('/signin');
  next();
};

export const requireNotAuth = async (to, from, next) => {
  // await store.dispatch(`${authModule}/${authActions.VALIDATE_TOKEN}`);
  // If user was routed to signin somehow from a route,
  // and they are still authenticated, keep them on their
  // current route.
  if (isUserAuthenticated() && from.name) next(from.name);
  // Otherwise route them to the dashboard.
  if (isUserAuthenticated() && !from.name) next('/dashboard');
  next();
};
