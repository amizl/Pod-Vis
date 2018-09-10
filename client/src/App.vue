<template lang="pug">
  v-app
    app-header(v-if='user')
    v-content(color='secondary')
      router-view
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
