<template>
  <v-container fluid fill-height>
    <v-row align="center" justify="center">
      <v-col cols="5">
	<v-sheet color="white" height="100%" class="rounded-lg shadow">
          <user-authentication />
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import UserAuthentication from '@/components/auth/UserAuthentication.vue';

export default {
  components: {
    UserAuthentication,
  },
};
</script>

<style scoped></style>
