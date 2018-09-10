<!--
TOOD:
  1. Fix transition/animation resize from login to create account
  2. Form validation in login/create account
-->
<template lang='pug'>
  v-flex(xs12 sm8 md4).elevation-3
    v-tabs(slider-color="secondary" grow)
      v-tab(key='login') SIGN IN
      v-tab(key='createAccount') CREATE ACCOUNT
      v-tabs-items.white
        v-alert(
        :value='authError'
        type='error'
        transition='fade-transition'
        ) {{ authError }}
        v-tab-item
          sign-in-form
        v-tab-item
          create-account-form

</template>

<script>
import SignIn from './SignIn.vue';
import CreateAccount from './CreateAccount.vue';

export default {
  data() {
    return {
    };
  },
  computed: {
    user() {
      return this.$store.getters.user;
    },
    authError() {
      return this.$store.getters.authError;
    },
  },
  watch: {
    user(value) {
      if (value !== null && value !== undefined) {
        this.$router.push('/');
      }
    },
  },
  components: {
    signInForm: SignIn,
    createAccountForm: CreateAccount,
  },
  methods: {
  },
};
</script>

<style scoped>
</style>
