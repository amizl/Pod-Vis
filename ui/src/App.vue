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
    <v-footer
      v-if="
        $route == null || $route.name == 'homepage' || $route.name == 'signIn'
      "
      class="indigo lighten-5"
    >
      <v-spacer></v-spacer>
      <div class="font-weight-medium">
        &copy; 2020 University of Maryland, Baltimore
      </div>
    </v-footer>
  </v-app>
</template>

<script>
import { mapGetters } from 'vuex';
import { getters as authGetters } from '@/store/modules/auth/types';
import SideBar from './components/layout/Sidebar.vue';
import NotificationCenter from './components/common/notificationCenter.vue';

// draggable dialog code from https://github.com/vuetifyjs/vuetify/issues/4058
(function() {
  // make vuetify dialogs movable
  const d = {};
  document.addEventListener('mousedown', e => {
    const closestDialog = e.target.closest('.v-dialog.v-dialog--active');
    if (
      e.button === 0 &&
      closestDialog != null &&
      e.target.classList.contains('v-card__title')
    ) {
      // element which can be used to move element
      d.el = closestDialog; // element which should be moved
      d.mouseStartX = e.clientX;
      d.mouseStartY = e.clientY;
      d.elStartX = d.el.getBoundingClientRect().left;
      d.elStartY = d.el.getBoundingClientRect().top;
      d.el.style.position = 'fixed';
      d.el.style.margin = 0;
      d.oldTransition = d.el.style.transition;
      d.el.style.transition = 'none';
    }
  });
  document.addEventListener('mousemove', e => {
    if (d.el === undefined) return;
    d.el.style.left =
      Math.min(
        Math.max(d.elStartX + e.clientX - d.mouseStartX, 0),
        window.innerWidth - d.el.getBoundingClientRect().width
      ) + 'px';
    d.el.style.top =
      Math.min(
        Math.max(d.elStartY + e.clientY - d.mouseStartY, 0),
        window.innerHeight - d.el.getBoundingClientRect().height
      ) + 'px';
  });
  document.addEventListener('mouseup', () => {
    if (d.el === undefined) return;
    d.el.style.transition = d.oldTransition;
    d.el = undefined;
  });
  setInterval(() => {
    // prevent out of bounds
    const dialog = document.querySelector('.v-dialog.v-dialog--active');
    if (dialog === null) return;
    dialog.style.left =
      Math.min(
        parseInt(dialog.style.left),
        window.innerWidth - dialog.getBoundingClientRect().width
      ) + 'px';
    dialog.style.top =
      Math.min(
        parseInt(dialog.style.top),
        window.innerHeight - dialog.getBoundingClientRect().height
      ) + 'px';
  }, 100);
})();

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
/* Global (mostly) font size setting */
html {
  font-size: 1em !important;
}

.v-application {
  font-size: 1.1rem !important;
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
  font-size: 1.2em;
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
