<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Dataset Manager</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        prepend-inner-icon="search"
        label="Search for Dataset"
        solo
        flat
        background-color="grey lighten-4"
        class="mt-2"
      >
      </v-text-field>
      <v-spacer></v-spacer>
      <v-toolbar-items class="hidden-sm-and-down">
        <v-btn
          :to="selectedDatasets | buildPath"
          :disabled="selectedDatasets.length === 0"
          flat
          right
        >
          <!-- <v-icon color="grey lighten-2" small fab left> build </v-icon> -->
          Create Collection</v-btn
        >
      </v-toolbar-items>
    </v-toolbar>
    <v-layout row justify-center>
      <v-flex xs12> <dataset-table :search="search" /> </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import Header from '@/components/layout/Header.vue';
import DatasetTable from '@/components/DatasetManager/DatasetTable.vue';
import OutcomeTable from '@/components/DatasetManager/OutcomeTable.vue';
import DemographicsTable from '@/components/DatasetManager/DemographicsTable.vue';
import FilterTree from '@/components/DatasetManager/FilterTree.vue';
//  import DonutChart from '@/components/charts/DonutChart.vue';

export default {
  components: {
    datasetTable: DatasetTable,
    // donutChart: DonutChart,
    contentHeader: Header,
    filterTree: FilterTree,
    OutcomeTable,
    DemographicsTable,
  },
  filters: {
    buildPath(datasets) {
      // This constructs the build path with selected dataset ids
      if (!datasets) return 'build';

      const idParams = datasets.map(dataset => `id=${dataset.id}`).join('&');
      return `datasets/build?${idParams}`;
    },
  },

  data() {
    return {
      snackbar: false,
      search: '',
    };
  },
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
    intersection() {
      // Compute the intersection of outcome
      // measures between selected datasets
      if (this.selectedDatasets.length < 2);
      // return [];

      const outcomeMeasures = this.selectedDatasets.map(
        ({ outcomes }) => outcomes.children
      );

      return outcomeMeasures.reduce((a, b) => a.filter(c => b.includes(c)));
    },
    intersectionExists() {
      return this.intersection.length > 0;
    },
    buildPathWithParams() {
      if (!this.selectedDatasets) return 'build';
      const idParams = this.selectedDatasets
        .map(dataset => dataset.id)
        .map(id => `id=${id}`)
        .join('&');

      return `'build?${idParams}`;
    },
    outcomeMeasures() {
      // Flatten array of outcome measures
      if (!this.selectedDatasets) return [];

      return this.selectedDatasets
        .map(d => d.variables) // get outcome measures
        .reduce((prev, curr) => prev.concat(curr)) // flatten
        .map(v => v.name); // get outcome measure name
    },
  },
  methods: {
    ...mapActions('datasetManager', {
      addSelectedDatasetsToCohorts: actions.ADD_SELECTED_DATASETS_TO_COHORTS,
    }),
  },
};
</script>

<style scoped>
div.v-dialog.v-bottom-sheet.v-bottom-sheet--inset.v-dialog--active {
  overflow: scroll;
}
</style>
