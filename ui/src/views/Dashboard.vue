<template>
  <v-container fluid>
    <v-toolbar extended app class="primary shadow send-to-back">
      <v-toolbar-title class="white--text">Dashboard</v-toolbar-title>
    </v-toolbar>
    <v-layout class="translate-up" fill-height>
      <!-- <v-layout align-center justify-center> -->
      <v-flex xs12>
        <v-card> <collection-table></collection-table> </v-card>
      </v-flex>
      <!-- <v-flex xs8> <v-card> </v-card> </v-flex> -->

      <!-- <h1 class="headline text-md-center">
        <v-icon large class="pb-4">build</v-icon><br />
        Dashboard is currently under development
      </h1> -->
    </v-layout>
    <!-- <v-layout align-center justify-center>
      <v-flex xs12> <dataset-table /> </v-flex>
    </v-layout> -->
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
    ...mapState('dashboard', {
      datasets: state.DATASETS,
      isLoading: state.IS_LOADING,
    }),
  },
  created() {
    if (!this.datasets.length) {
      this.fetchDatasets();
    }
  },
  methods: {
    ...mapActions('dashboard', {
      fetchDatasets: actions.FETCH_DATASETS,
    }),
  },
};
</script>

<style scoped></style>
