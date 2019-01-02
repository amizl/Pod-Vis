<template>
  <v-app>
    <app-side-bar v-if="isUserAuthenicated"></app-side-bar>
    <v-content>
      <transition name="fade" mode="out-in">
        <router-view></router-view>
      </transition>
    </v-content>
  </v-app>
</template>
<script>
import { createNamespacedHelpers } from 'vuex';
import { state } from '@/store/modules/auth/types';
import Footer from './components/layout/Footer.vue';
import SideBar from './components/layout/Sidebar.vue';
import SignIn from './views/SignIn.vue';

const { mapState } = createNamespacedHelpers('auth');

export default {
  name: 'App',
  components: {
    appFooter: Footer,
    signInForm: SignIn,
    appSideBar: SideBar,
  },
  data() {
    return {};
  },
  computed: {
    ...mapState({
      user: state.USER,
    }),
    isUserAuthenicated() {
      return this.user !== null && this.user !== undefined;
    },
  },
  watch: {},
  beforeUpdate() {
    this.redirectUserIfNotAuth();
  },
  methods: {
    redirectUserIfNotAuth() {
      if (!this.isUserAuthenicated) {
        this.$router.push('/signin');
      }
    },
  },
};
</script>

<style scoped>
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
