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
const isUserAuthenticated = () =>
  store.getters[`${authModule}/${authGetters.IS_USER_AUTHENTICATED}`];

export const requireAuth = async (to, from, next) => {
  try {
    await store.dispatch(`${authModule}/${authActions.VALIDATE_TOKEN}`);
    next();
  } catch (err) {
    next('/signin');
  }
};

export const requireNotAuth = async (to, from, next) => {
  // If user was routed to signin somehow from a route,
  // and they are still authenticated, keep them on their
  // current route.
  // Otherwise route them to the dashboard.
  try {
    await store.dispatch(`${authModule}/${authActions.VALIDATE_TOKEN}`);
    if (isUserAuthenticated() && from.name) next(from.name);
    if (isUserAuthenticated() && !from.name) next('/dashboard');
  } catch (err) {
    next();
  }
};
