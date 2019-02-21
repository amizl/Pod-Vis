<!--
TOOD:
  1. Form validation in login/create account
-->
<template lang="pug">
  v-tabs(slider-color="secondary" grow)
    v-tab(key='login') SIGN IN
    v-tab(key='createAccount') CREATE ACCOUNT
    v-tabs-items
      v-alert(
        :value='authError'
        type='error'
        transition='fade-transition'
        dismissible
      ) {{ authError }}
      v-tab-item
        sign-in-form
      v-tab-item
        create-account-form

</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/auth/types';
import SignIn from './SignIn.vue';
import CreateAccount from './CreateAccount.vue';

export default {
  components: {
    signInForm: SignIn,
    createAccountForm: CreateAccount,
  },
  data() {
    return {};
  },
  computed: {
    ...mapState('auth', {
      user: state.USER,
      authError: state.AUTH_ERROR,
    }),
  },
  watch: {
    user(value) {
      if (value !== null && value !== undefined) {
        this.$router.push('/');
      }
    },
  },
};
</script>

<style scoped></style>
