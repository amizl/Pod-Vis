<template lang='pug'>
  v-container(fluid fill-height)
    v-layout(align-center justify-center)
      v-flex(xs12 sm8 md4).elevation-3
        user-authentication
</template>

<script>
import UserAuthentication from '../components/UserAuthentication.vue';

export default {
  components: {
    UserAuthentication,
  },
};
</script>

<style scoped>
</style>
