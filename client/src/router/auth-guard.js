import { getters } from '../store/modules/auth/types';
import store from '../store';

export default (to, from, next) => {
  if (store.getters[`auth/${getters.USER}`]) {
    next();
  } else {
    next('/signin');
  }
};
