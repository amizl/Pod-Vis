<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Create Cohort</v-toolbar-title>
      <v-spacer></v-spacer>
    </v-toolbar>
    <v-layout align-center justify-center>
      <h1 class="headline text-md-center">
        <v-icon large class="pb-4">build</v-icon><br />
        Creating a cohort is currently under development
      </h1>
    </v-layout>
  </v-container>
</template>

<script>
// import { mapState, mapActions } from 'vuex';
// import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  props: {
    // id is passed in via route parameters
    // i.e., /build?id=x&id=y
    id: {
      type: [String, Array],
      default: null,
    },
  },
  computed: {},
  methods: {},
};
</script>

<style scoped></style>
