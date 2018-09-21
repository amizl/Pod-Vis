<template lang="pug">
  v-app
    app-header(v-if='isUserAuthenicated')
    v-content(color='secondary')
        router-view
    //- v-footer(app dense dark).primary
</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import Header from './components/Header.vue';
import SignIn from './views/SignIn.vue';
import { GETTERS } from '@/store/modules/auth/types';

const { mapGetters } = createNamespacedHelpers('auth');

export default {
  components: {
    appHeader: Header,
    signInForm: SignIn,
  },
  name: 'App',
  data() {
    return {
    };
  },
  computed: {
    ...mapGetters({
      user: GETTERS.USER,
    }),
    isUserAuthenicated() {
      return this.user !== null && this.user !== undefined;
    },
  },
  watch: {
  },
  methods: {
    redirectUserIfNotAuth() {
      if (this.user === null || this.user === undefined) {
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
