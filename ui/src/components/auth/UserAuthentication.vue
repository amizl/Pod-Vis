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
import { mapState, mapGetters } from 'vuex';
import { state, getters } from '@/store/modules/auth/types';
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
      authError: state.AUTH_ERROR,
    }),
    ...mapGetters('auth', {
      isUserAuthenticated: getters.IS_USER_AUTHENTICATED,
    }),
  },
};
</script>

<style scoped></style>
