import '@babel/polyfill';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import { actions as authActions } from '@/store/modules/auth/types';
import Vue from 'vue';
import './plugins/vuetify';
import App from './App.vue';
import store from './store';
import router from './router';

require('./assets/css/main.css');
require('parcoord-es/dist/parcoords.css');

// Globally register the loading spinner because we
// use it in so many components.
Vue.component('loading-spinner', LoadingSpinner);

const authModule = 'auth';
const getUserFromSession = authActions.GET_USER_FROM_SESSION;
// This step is important. We want to wait for the store to be
// initialized and user data to be fetched before we initialize
// the application. Because checking if the user is already logged
// in is an asynchronous call, we want to wait until it finishes
// so our app can appropriately give access to certain pages.
(async () => {
  try {
    await store.dispatch(`${authModule}/${getUserFromSession}`);
  } catch (err) {
    // No active user token
  } finally {
    // Init app and mount to the DOM
    new Vue({
      store,
      router,
      render: h => h(App),
    }).$mount('#app');
  }
})();
