<template lang='pug'>
  v-card
    v-card-text
      v-form
        v-text-field(
          prepend-icon="person"
          v-model='fullName'
          name="fullName"
          label="Full Name"
          type="text"
          placeholder="John Doe"
          :rules="[() => !!fullName || 'This field is required']"
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
          required
        )
        v-text-field(
          prepend-icon="email"
          v-model='email'
          name="email"
          label="E-mail"
          type="text"
          hint='This will be your username to log in'
          placeholder='john.doe@gmail.com'
          :rules="[() => !!email || 'This field is required']"
          :error-messages="errorMessages"
          required
        )
        v-text-field(
          id="password"
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
          id="password"
          v-model='confirmPassword'
          prepend-icon=" "
          name="confirmPassword"
          label="Confirm Password"
          type="password"
          :rules="[() => !!confirmPssword || 'Please confirm password']"
          :error-messages="errorMessages"
          required
        )
    v-card-actions
      v-spacer
      v-btn(color='primary') Create Account
</template>

<script>
export default {
  data() {
    return {
      fullName: null,
      institution: null,
      email: null,
      password: null,
      confirmPassword: null,
      errorMessages: '',
      formHasErrors: false,
    };
  },
};
</script>

<style>
</style>
