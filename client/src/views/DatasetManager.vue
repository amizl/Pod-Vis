<template>
  <div>
    <!-- <v-toolbar class="white" app>
      <v-layout>
        <v-flex xs6>
          <v-text-field
            v-model="search"
            prepend-inner-icon="search"
            label="Search for Dataset"
            solo
            flat
            background-color="background"
            class="mt-2"
          >
          </v-text-field>
        </v-flex>
        <v-flex xs6> </v-flex>
      </v-layout>
      <v-btn
        :to="selectedDatasets | buildPath"
        :disabled="selectedDatasets.length === 0"
        append
        class="primary"
      >
        <v-icon color="iconColor" small fab left> build </v-icon>
        BUILD DATASET
      </v-btn>
    </v-toolbar> -->
    <!-- <div class="white--text blueGradient">
      <v-container fluid>
        <v-layout row wrap>
          <v-flex xs6>
            <p class="headline font-weight-medium">Dataset Manager</p>
          </v-flex>
          <v-flex xs6>
            <v-layout row>
              <v-flex xs6> </v-flex>
              <v-flex xs6> </v-flex>
            </v-layout>
          </v-flex>
        </v-layout>
      </v-container>
    </div> -->
    <v-container fluid>
      <v-layout class="mt-4" justify-center>
        <v-flex xs10>
          <v-layout>
            <v-flex xs6> <p class="headline">Dataset Manager</p> </v-flex>
            <v-flex xs6 class="text-xs-right">
              <v-btn
                :to="selectedDatasets | buildPath"
                :disabled="selectedDatasets.length === 0"
                flat
                right
              >
                <!-- <v-icon color="grey lighten-2" small fab left> build </v-icon> -->
                Build Dataset</v-btn
              >
            </v-flex>
          </v-layout>
          <v-divider></v-divider>
        </v-flex>
      </v-layout>
      <v-layout class="pt-5" row justify-center>
        <v-flex xs10>
          <p class="subheading foo--text">Available Datasets</p>
          <dataset-table :search="search"></dataset-table>
        </v-flex>
      </v-layout>
      <!-- <v-snackbar
        v-model='snackbar'
        :color="intersectionExists ? 'success' : 'error'"
        :multi-line="!intersectionExists"
        :timeout=10000
      >
        <v-card
          flat
          :color="intersectionExists ? 'success' : 'error'"
          class="white--text"
        >
          <v-card-text>
            Selected datasets have no shared outcome measures
          </v-card-text>
        </v-card>
        <v-btn
          dark
          flat
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </v-snackbar> -->
    </v-container>
  </div>
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

      const idParams = datasets
        .map(dataset => dataset.id)
        .map(id => `id=${id}`)
        .join('&');

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
    watch: {
      intersection(matches) {
        // We want to watch our computed intersection
        // and check if it is returning matches. If there
        // are matches then this means they share outcome
        // measures
        if (this.selectedDatasets.length > 1) {
          this.snackbar = true;
        }
      },
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
