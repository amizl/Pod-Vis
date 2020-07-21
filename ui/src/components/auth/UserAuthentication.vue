<template>
  <div>
    <v-tabs v-model="tab" slider-color="primary" grow class="rounded-lg">
      <v-tab class="primary--text">SIGN IN</v-tab>
      <v-tab class="primary--text">CREATE ACCOUNT</v-tab>
    </v-tabs>

    <v-tabs-items v-model="tab">
      <v-alert
        :value="authError"
        type="error"
        transition="fade-transition"
        dismissable
      >
        {{ authError }}
      </v-alert>
      <v-tab-item> <sign-in-form /> </v-tab-item>
      <v-tab-item> <create-account-form /> </v-tab-item>
    </v-tabs-items>
  </div>
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
    return { tab: null };
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
