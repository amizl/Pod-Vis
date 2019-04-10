import '@babel/polyfill';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import * as firebase from 'firebase';
import Vue from 'vue';
import { mapActions } from 'vuex';
import './plugins/vuetify';
import App from './App.vue';
import router from './router';
import store from './store';
import { actions } from './store/modules/auth/types';

require('./assets/css/main.css');
require('parcoord-es/dist/parcoords.css');

Vue.config.productionTip = false;
// Globally register the loading spinner because we
// use it in so many components.
Vue.component('loading-spinner', LoadingSpinner);

new Vue({
  router,
  store,
  created() {
    firebase.initializeApp({
      apiKey: 'AIzaSyCgV1G2UfTJ1-O0KeM677Uy93znHEesl2g',
      authDomain: 'cliovis-cb0c9.firebaseapp.com',
      databaseURL: 'https://cliovis-cb0c9.firebaseio.com',
      projectId: 'cliovis-cb0c9',
      storageBucket: 'cliovis-cb0c9.appspot.com',
    });

    firebase.firestore().settings({
      timestampsInSnapshots: true,
    });
    // When the app is first loaded, we first want to check if there is an
    // active user session. If so, we can consider the user is still logged
    // in and route the user to their dashboard.
    this.getUserIfSessionActive();
  },
  methods: {
    ...mapActions('auth', {
      getUserIfSessionActive: actions.GET_USER_FROM_SESSION,
    }),
  },
  render: h => h(App),
}).$mount('#app');
