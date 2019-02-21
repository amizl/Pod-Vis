<template>
  <v-container fluid>
    <v-toolbar class="background" flat app></v-toolbar>
    <v-layout justify-center>
      <v-flex xs10>
        <p class="display-1 foo--text">Dashboard</p>
        <v-divider></v-divider>
      </v-flex>
    </v-layout>
    <v-layout class="pt-5" align-center justify-center>
      <v-flex xs10>
        <p class="subheading foo--text">My Datasets</p>
        <dataset-table></dataset-table>
        <!-- <v-card>
            <v-card-title></v-card-title>
            <v-card-text> </v-card-text>
          </v-card> -->
      </v-flex>
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
