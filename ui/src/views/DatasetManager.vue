<template>
  <v-container fluid class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Dataset Manager - Create New Study Dataset
        <div class="subheading">Choose Datasets</div>
      </v-toolbar-title>

      <v-spacer></v-spacer>
      <!-- <v-text-field
        v-model="search"
        prepend-inner-icon="search"
        label="Search for Dataset"
        solo
        flat
        background-color="grey lighten-4"
        class="mt-2"
      >
      </v-text-field> -->
      <v-spacer></v-spacer>
      <!-- <v-toolbar-items class="hidden-sm-and-down"> -->
      <v-btn
        color="primary--text"
        :to="selectedDatasets | buildPath"
        :disabled="selectedDatasets.length === 0"
        right
      >
        <!-- <v-icon color="grey lighten-2" small fab left> build </v-icon> -->
        Select Variables</v-btn
      >
      <!-- </v-toolbar-items> -->
    </v-toolbar>

    <v-sheet color="white" height="100%" class="scroll rounded-lg shadow">
      <analysis-tracker step="2" substep="2.1"></analysis-tracker>
    </v-sheet>

    <v-layout fill-height justify-center class="mt-2">
      <v-flex xs12 class="pa-0 ma-0">
        <v-card class="shadow rounded-lg">
          <v-tabs slider-color="primary" grow>
            <v-tab>
              <span class="">Available Datasets</span>
              <!-- <span class="subheading grey--text lighten-2"
                  >Select those you wish to combine.</span
                > -->
            </v-tab>
            <v-tab-item> <dataset-table :search="search" /> </v-tab-item>
          </v-tabs>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import DatasetTable from '@/components/DatasetManager/DatasetTable.vue';

export default {
  components: {
    AnalysisTracker,
    DatasetTable,
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
      activeTab: '',
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
