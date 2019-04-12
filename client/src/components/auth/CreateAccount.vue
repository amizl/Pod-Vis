<template lang="pug">
  v-card(flat)
    v-card-text
      v-form(ref='form' @submit.prevent='onCreateAccount').ma-4
        v-text-field(
          prepend-icon="person"
          v-model='name'
          name="name"
          label="Full Name"
          type="text"
          placeholder="John Doe"
          :rules="[() => !!name || 'This field is required']"
          :error-messages="errorMessages"
          required)
        v-text-field(
          prepend-icon="email"
          v-model='email'
          name="email"
          label="Email"
          type="text"
          placeholder='john.doe@gmail.com'
          :rules="[() => !!email || 'This field is required']"
          :error-messages="errorMessages"
          required
        )
        v-text-field(
          prepend-icon="business_center"
          v-model='institution'
          name="institution"
          label="Institution"
          type="text"
          placeholder="University of Maryland School of Medicine"
          required)
        v-text-field(
          v-model='password'
          prepend-icon="lock"
          name="password"
          label="Password"
          type="password"
          :rules="[() => !!password || 'This field is required']"
          :error-messages="errorMessages"
          required
        )
        v-text-field(
          v-model='confirmPassword'
          prepend-icon=" "
          name="confirmPassword"
          label="Confirm Password"
          type="password"
          :rules="[() => !!confirmPassword || 'Please confirm password', comparePasswords]"
          :error-messages="errorMessages"
          required)
        v-card-actions
          v-spacer
          v-btn(
            type='submit'
            color='primary'
            :loading='loading'
            :disabled='loading'
          ) Create Account
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
      name: '',
      email: '',
      institution: '',
      password: '',
      confirmPassword: '',
      errorMessages: '',
    };
  },
  computed: {
    comparePasswords() {
      return this.password !== this.confirmPassword
        ? 'Passwords do not match.'
        : '';
    },
    ...mapState('auth', {
      loading: authState.IS_LOADING,
    }),
  },
  methods: {
    ...mapActions('auth', {
      createUserAccount: authActions.CREATE_USER_ACCOUNT,
    }),
    onCreateAccount() {
      if (this.$refs.form.validate()) {
        this.createUserAccount({
          name: this.name,
          email: this.email,
          institution: this.institution,
          password: this.password,
        })
          .then(() => {
            // If creating account is successful, redirect user to dashboard
            this.$router.push('/dashboard');
          })
          .catch(() => {
            // Currently do nothing here if creating account is unsuccessful.
            // The Auth Store will set an error which will be automatically
            // display on the DOM.
          });
      }
    },
  },
};
</script>

<style></style>
