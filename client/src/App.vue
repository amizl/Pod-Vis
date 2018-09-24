<template lang="pug">
  v-app
    app-side-bar(v-if='isUserAuthenicated')
    v-content(color='secondary')
        router-view
    app-footer
</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import { getters } from '@/store/modules/auth/types';
import Footer from './components/layout/Footer.vue';
import SideBar from './components/layout/Sidebar.vue';
import SignIn from './views/SignIn.vue';

const { mapGetters } = createNamespacedHelpers('auth');

export default {
  components: {
    appFooter: Footer,
    signInForm: SignIn,
    appSideBar: SideBar,
  },
  name: 'App',
  data() {
    return {
    };
  },
  computed: {
    ...mapGetters({
      user: getters.USER,
    }),
    isUserAuthenicated() {
      return this.user !== null && this.user !== undefined;
    },
  },
  watch: {
  },
  methods: {
    redirectUserIfNotAuth() {
      if (!this.isUserAuthenicated) {
        this.$router.push('/signin');
      }
    },
  },
  beforeUpdate() {
    this.redirectUserIfNotAuth();
  },
};
</script>

<style scoped>

</style>
