<template lang='pug'>
  v-card
    v-card-text
      v-form(@submit.prevent='onSignIn').ma-4
        v-text-field(
          v-model='email'
          prepend-icon="person"
          name="email"
          label="Email"
          type="text"
        )
        v-text-field(
          v-model='password'
          prepend-icon="lock"
          name="password"
          label="Password"
          type="password"
        )
        v-card-actions
          v-spacer
          v-btn(
            type='submit'
            color='primary'
            :disabled='loading'
            :loading='loading'
          ) Sign In
            span(slot='loader') Signing in
</template>

<script>
export default {
  data() {
    return {
      email: null,
      password: null,
      signInError: false,
    };
  },
  computed: {
    loading() {
      return this.$store.getters.loading;
    },
  },
  methods: {
    onSignIn() {
      this
        .$store
        .dispatch('signUserIn', {
          email: this.email,
          password: this.password,
        });
    },
  },
};
</script>

<style>
</style>
