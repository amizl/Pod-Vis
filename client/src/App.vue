<template lang="pug">
  v-app
    app-header(v-if='isUserAuthenicated')
    v-content(color='secondary')
        router-view
    //- v-footer(app dense dark).primary
</template>

<script>
import Header from './components/Header.vue';
import SignIn from './views/SignIn.vue';

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
    user() {
      return this.$store.getters.user;
    },
    isUserAuthenicated() {
      return this.$store.getters.user !== null &&
        this.$store.getters.user !== undefined;
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
