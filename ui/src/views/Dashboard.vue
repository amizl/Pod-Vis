<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Dashboard</v-toolbar-title>
    </v-toolbar>
    <v-layout align-center justify-center>
      <v-flex xs12>
        <v-card> <collection-table></collection-table> </v-card>
      </v-flex>

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

import CollectionTable from '@/components/common/CollectionTable.vue';
import DatasetTable from '@/components/dashboard/DatasetTable.vue';

export default {
  components: {
    CollectionTable,
    DatasetTable,
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
