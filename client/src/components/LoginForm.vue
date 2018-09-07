<template lang='pug'>
  v-card
    //- v-toolbar(dense flat dark color='primary')
    //-   v-toolbar-header LOGIN
    v-card-text
      v-form
        v-text-field(prepend-icon="person" name="email" label="E-mail" type="text")
        v-text-field(id="password" prepend-icon="lock" name="password" label="Password" type="password")
    v-card-actions
      v-spacer
      v-btn(color='primary') Log In
</template>

<script>
export default {
};
</script>

<style>
</style>
