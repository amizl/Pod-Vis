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
    loading() {
      return this.$store.getters.loading;
    },
  },
  methods: {
    onSignIn() {
      if (this.$refs.form.validate()) {
        this
          .$store
          .dispatch('signUserIn', {
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
