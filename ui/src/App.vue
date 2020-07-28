<template>
  <v-app id="app">
    <!-- Notification Center is our global snackbar for error/success messages-->
    <notification-center />
    <side-bar v-if="isUserAuthenticated" />
    <!-- <app-header v-if="isUserAuthenticated" /> -->
    <!-- All of our views will be loaded inside content based on route-->
    <v-main class="indigo lighten-5">
      <transition name="fade" mode="out-in">
        <!-- /homepage, /datasets, etc. components to be injected here -->
        <router-view />
      </transition>
    </v-main>
    <v-footer class="indigo lighten-5" v-if="($route == null) || ($route.name == 'homepage') || ($route.name == 'signIn')"> 
      <v-spacer></v-spacer>
      <div class="font-weight-medium">&copy; 2020 University of Maryland, Baltimore</div>
    </v-footer>
  </v-app>
</template>

<script>
import { mapGetters } from 'vuex';
import { getters as authGetters } from '@/store/modules/auth/types';
import SideBar from './components/layout/Sidebar.vue';
import NotificationCenter from './components/common/notificationCenter.vue';

export default {
  name: 'App',
  components: {
    SideBar,
    NotificationCenter,
  },
  computed: {
    ...mapGetters('auth', {
      isUserAuthenticated: authGetters.IS_USER_AUTHENTICATED,
    }),
  },
};
</script>

<style>

/* Global (sort of) font size setting */
.v-application {
    font-size: 1.2em !important;
}

/* Circled number in stepper step */
span.v-stepper__step__step {
  font-size: 1em;
  width: 35px;
  height: 35px;
}

/* Lines connecting steps in the v-stepper */
div.v-stepper__header hr.v-divider.theme--light {
  border-top-width: 3px;
  border-top-color: rgba(0, 0, 0, 0.35) !important;
}

/* Dataset Overview page - SunBurst chart and heading div */
div.v-card__text {
  font-size: 1.1em;
}

/* Increase font size of D3 axis labels - CohortManager charts */
g.tick text {
  font-size: 1.3em;
}

/* Transition effect for changing routes */
.fade-enter-active,
.fade-leave-active {
  transition-duration: 0.3s;
  transition-property: opacity;
  transition-timing-function: ease;
}
.fade-enter,
.fade-leave-active {
  opacity: 0;
}
</style>
