<template>
  <v-app>
    <!-- Notification Center is our global snackbar for error/success messages-->
    <notification-center />
    <side-bar v-if="isUserAuthenticated" />
    <!-- <app-header v-if="isUserAuthenticated" /> -->
    <!-- All of our views will be loaded inside content based on route-->
    <v-content class="indigo lighten-5">
      <transition name="fade" mode="out-in">
        <!-- /homepage, /datasets, etc. components to be injected here -->
        <router-view />
      </transition>
    </v-content>
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

/* Increase font sizes throughout the app (modifying main.styl has no effect in 1.5) */

html {
  font-size: 1.2em;
}

/* v-datatable */
table.v-datatable td.text-xs-left {
  font-size: 1em;
}

table.v-datatable td.text-xs-center {
  font-size: 1em;
}

table.v-datatable td.text-xs-right {
  font-size: 1em;
}

table.v-datatable td div {
  font-size: 1.2em;
}

table.v-datatable td span {
  font-size: 1.4em;
}

table.v-datatable div.v-btn__content {
  font-size: 1.2em;
}

div.v-btn__content {
  font-size: 1.2em;
}

div.v-datatable__actions {
  font-size: 1.2em;
}

span.subheading {
  font-size: 1.5em;
}

span.subtitle-1 {
  font-size: 1.2em;
}

/* Sidebar navigation options */
div.v-list__tile__title {
  font-size: 1.2em;
}

/* Stepper labels */
div.v-stepper__label {
  font-size: 0.9em;
}

/* Circled number in stepper step */
span.v-stepper__step__step {
  font-size: 1em;
}

/* Dataset Overview page */
div.v-card__text {
  font-size: 1.2em;
}

div.v-treeview-node__label {
  font-size: 1em;
}

table.v-datatable div.layout.align-center {
  font-size: 1.4em;
}

table.v-datatable span {
  font-size: 1.4em;
}

/* title/heading of tabs in v-datatable */
div.v-tabs__div {
  font-size: 1.2em;
}

/* larger font for data table headings */
table.v-table thead th {
  font-size: 20px !important;
}

/* Increase font size of D3 axis labels */
g.tick text {
 font-size: 1.2em;
}

svg {
 font-size: 2em;
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
