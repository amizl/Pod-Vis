<template lang='pug'>
  v-container(fluid fill-height)
    v-layout(align-center justify-center)
      login-create
</template>

<script>
import LoginCreateForms from '../components/LoginOrCreateCard.vue';

export default {
  components: {
    loginCreate: LoginCreateForms,
  },
};
</script>

<style scoped>
</style>
