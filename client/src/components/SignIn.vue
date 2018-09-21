<template lang='pug'>
  v-card
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
            span(slot='loader') Signing in
</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import { GETTERS, ACTIONS } from '@/store/modules/auth/types';

const { mapGetters, mapActions } = createNamespacedHelpers('auth');

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
    ...mapGetters({
      loading: GETTERS.LOADING,
    }),
  },
  methods: {
    ...mapActions({
      signUserIn: ACTIONS.SIGN_USER_IN,
    }),
    onSignIn() {
      if (this.$refs.form.validate()) {
        this.signUserIn({
          email: this.email,
          password: this.password,
        });
      }
    },
  },
};
</script>

<style>
</style>
