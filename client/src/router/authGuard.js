import { state } from '../store/modules/auth/types';
import store from '../store';

export default (to, from, next) => {
  if (store.state.auth[state.USER]) {
    next();
  } else {
    next('/signin');
  }
};
