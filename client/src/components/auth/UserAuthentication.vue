<!--
TOOD:
  1. Fix transition/animation resize from login to create account
  2. Form validation in login/create account
-->
<template lang='pug'>
  v-tabs(slider-color="secondary" grow)
    v-tab(key='login') SIGN IN
    v-tab(key='createAccount') CREATE ACCOUNT
    v-tabs-items
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
import { createNamespacedHelpers } from 'vuex';
import { getters } from '@/store/modules/auth/types';
import SignIn from './SignIn.vue';
import CreateAccount from './CreateAccount.vue';

const { mapGetters } = createNamespacedHelpers('auth');

export default {
  data() {
    return {
    };
  },
  computed: {
    ...mapGetters({
      user: getters.USER,
      authError: getters.AUTH_ERROR,
    }),
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
