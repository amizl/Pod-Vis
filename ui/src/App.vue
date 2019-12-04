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
