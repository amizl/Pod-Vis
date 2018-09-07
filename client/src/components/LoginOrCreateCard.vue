<!--
TOOD:
  1. Fix transition/animation resize from login to create account
  2. Form validation in login/create account
-->
<template lang='pug'>
  v-flex(xs12 sm8 md4)
    v-tabs(
      v-model="active"
      color='primary'
      dark
      slider-color="white"
    )
      v-tab(key='login') LOGIN
      v-tab(key='create') CREATE ACCOUNT
      v-tabs-items.white.elevation-12
        v-tab-item
          login-form
        v-tab-item
          create-account-form
</template>

<script>
import LoginForm from './LoginForm.vue';
import CreateAccountForm from '../CreateAccountForm.vue';

export default {
  components: {
    loginForm: LoginForm,
    createAccountForm: CreateAccountForm,
  },
};
</script>

<style scoped>
</style>
