<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md4>
        <v-card flat class="rounded-lg shadow">
          <user-authentication />
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import UserAuthentication from "@/components/auth/UserAuthentication.vue";

export default {
  components: {
    UserAuthentication
  }
};
</script>

<style scoped></style>
