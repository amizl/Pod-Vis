import '@babel/polyfill';
import Vue from 'vue';
import * as firebase from 'firebase';
import { createNamespacedHelpers } from 'vuex';
import './plugins/vuetify';
import App from './App.vue';
import router from './router';
import store from './store';
import { actions } from './store/modules/auth/types';

const { mapActions } = createNamespacedHelpers('auth');

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App),
  created() {
    firebase.initializeApp({
      apiKey: 'AIzaSyCgV1G2UfTJ1-O0KeM677Uy93znHEesl2g',
      authDomain: 'cliovis-cb0c9.firebaseapp.com',
      databaseURL: 'https://cliovis-cb0c9.firebaseio.com',
      projectId: 'cliovis-cb0c9',
      storageBucket: 'cliovis-cb0c9.appspot.com',
    });

    firebase
      .firestore()
      .settings({
        timestampsInSnapshots: true,
      });

    // Check if user session is still cached
    // and proceed to auto sign in
    firebase
      .auth()
      .onAuthStateChanged((user) => {
        if (user) {
          this.autoSignIn(user);
        }
      });
  },
  methods: {
    ...mapActions({
      autoSignIn: actions.AUTO_SIGN_IN,
    }),
  },
}).$mount('#app');
