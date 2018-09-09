<template lang='pug'>
  v-card
    v-card-text
      v-form(@submit.prevent='onCreateAccount').ma-4
        // v-text-field(
          prepend-icon="person"
          v-model='fullName'
          name="fullName"
          label="Full Name"
          type="text"
          placeholder="John Doe"
          :rules="[() => !!fullName || 'This field is required']"
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
        // v-text-field(
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
        // v-text-field(
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
            :disabled='loading'
            :loading='loading'
          ) Create Account
            span(slot='loader') Creating Account
</template>

<script>
export default {
  data() {
    return {
      // fullName: '',
      // institution: '',
      email: '',
      password: '',
      // confirmPassword: '',
      errorMessages: '',
    };
  },
  computed: {
    // comparePasswords() {
    //   return this.password !== this.confirmPassword ? 'Passwords do not match.': '';
    // },
      loading() {
        return this.$store.getters.loading;
      },
  },
  methods: {
    onCreateAccount() {
      // console.log({
      //   fn: this.fullName,
      //   int: this.institution,
      //   email: this.email,
      //   pw: this.password,
      // });
      this
        .$store
        .dispatch('createUserAccount', {
          email: this.email,
          password: this.password,
        })
    }
  }
};
</script>

<style>
</style>
