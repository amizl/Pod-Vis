<template lang='pug'>
  v-container(fluid fill-height)
    v-layout(align-center justify-center)
      v-flex(xs12 sm8 md4)
        v-card.elevation-12
          v-toolbar(dark color='primary')
            v-toolbar-title Login form
            v-card-text
              v-form
                v-text-field(prepend-icon="person" name="login" label="Login" type="text")
                v-text-field(id="password" prepend-icon="lock" name="password" label="Password" type="password")
            v-card-actions
              v-spacer
              v-btn(color='primary') Login
</template>

<script>
export default {
};
</script>

<style>
</style>

