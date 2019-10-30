<template>
  <v-container fluid>
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Dashboard</v-toolbar-title>
    </v-toolbar>
    <v-layout fill-height>
      <!-- <v-layout align-center justify-center> -->
      <v-flex xs12>
        <v-card flat class="rounded-lg shadow">
          <v-card-title class="title primary--text">Clinical Data Collections</v-card-title>
          <collection-table class="pb-1"></collection-table>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dashboard/types';

import CollectionTable from '@/components/dashboard/CollectionTable.vue';

export default {
  components: {
    CollectionTable,
  },
  computed: {
  },
  created() {
  },
  methods: {
  },
};
</script>

<style scoped></style>
