<template lang="pug">
  v-container(fluid fill-height)
    v-layout(align-center justify-center)
      v-flex(xs12 sm8 md4)
        v-card.ui-card.pa-1
          user-authentication
</template>

<script>
import UserAuthentication from '../components/auth/UserAuthentication.vue';

export default {
  components: {
    UserAuthentication,
  },
};
</script>

<style scoped></style>
