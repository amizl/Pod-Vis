<template lang="pug">
  v-card(flat).rounded-lg
    v-card-text
      v-form(ref='form' v-model='valid' @submit.prevent='onSignIn' lazy-validation).ma-4
        v-text-field(
          v-model='email'
          prepend-icon="person"
          name="email"
          label="Email"
          type="text"
          :rules="[() => !!email || 'This field is required']"
          required
        )
        v-text-field(
          v-model='password'
          prepend-icon="lock"
          name="password"
          label="Password"
          type="password"
          :rules="[() => !!password || 'This field is required']"
          required
        )
        v-card-actions
          v-spacer
          v-btn(
            type='submit'
            color='primary'
            disabled=true
            :disabled='loading'
            :loading='loading'
          ) Sign In
</template>

<script>
import { mapState, mapActions } from 'vuex';
import {
  state as authState,
  actions as authActions,
} from '@/store/modules/auth/types';

export default {
  data() {
    return {
      valid: true,
      email: null,
      password: null,
      signInError: false,
    };
  },
  computed: {
    ...mapState('auth', {
      loading: authState.IS_LOADING,
    }),
  },
  methods: {
    ...mapActions('auth', {
      signUserIn: authActions.SIGN_USER_IN,
    }),
    /**
     * Sign the user in after form submit.
     */
    onSignIn() {
      const { email, password } = this;
      if (this.$refs.form.validate()) {
        this.signUserIn({ email, password })
          .then(() => {
            // If signing in is successful, redirect user to dashboard
            this.$router.push('/dashboard');
          })
          .catch(() => {
            // Currently do nothing here if sign in is unsuccessful.
            // The Auth Store will set an error which will be automatically
            // display on the DOM.
          });
      }
    },
  },
};
</script>

<style></style>
