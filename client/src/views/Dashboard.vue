<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Dashboard</v-toolbar-title>
    </v-toolbar>
    <v-layout align-center justify-center>
      <v-flex xs12> <dataset-table /> </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dashboard/types';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import DatasetTable from '@/components/dashboard/DatasetTable.vue';

export default {
  components: {
    LoadingSpinner,
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
