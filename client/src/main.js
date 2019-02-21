import '@babel/polyfill';
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

new Vue({
  router,
  store,
  created() {
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
