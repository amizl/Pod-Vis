<template>
  <v-container fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>library_add</v-icon>
      <v-toolbar-title class="white--text pl-3"
        >Create New Study Dataset - Choose Datasets
        <div class="subtitle-1">Dataset: New Study Dataset (not saved)</div>
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

      <v-btn
        color="primary--text"
        :to="selectedDatasets | buildPath"
        :disabled="selectedDatasets.length === 0"
        right
      >
        Select Variables</v-btn
      >
    </v-app-bar>

    <analysis-tracker step="2" substep="2.1"></analysis-tracker>

    <v-container fluid fill-width class="ma-0 pa-0 pt-2">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-sheet color="white" height="100%" class="rounded-lg shadow">
            <v-card color="#eeeeee">
              <v-card-title class="primary--text pl-3"
                >Available Datasets
              </v-card-title>
            </v-card>

            <dataset-table :search="search" />
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>
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
