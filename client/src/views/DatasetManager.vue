<template>
  <div>
    <v-toolbar class="white" app>
      <v-layout>
        <v-flex xs6>
          <v-text-field
            v-model="search"
            prepend-inner-icon="search"
            label="Search for Dataset"
            solo
            flat
            background-color="bgColor"
            class="mt-2"
          >
          </v-text-field>
        </v-flex>
        <v-flex xs6>
        </v-flex>
      </v-layout>
        <v-btn
          append
          :to="selectedDatasets | buildPath"
          :disabled="selectedDatasets === null"
          class="primary"
        >
          <v-icon fab left> build </v-icon>
          BUILD DATASET
        </v-btn>
    </v-toolbar>
    <v-layout id='foo' row app class='primary white--text'>
      <v-container fluid>
        <v-flex xs12>
          <p class='headline'>DATASET MANAGER</p>
        </v-flex>

      </v-container>
    </v-layout>
    <v-container fluid>
      <v-layout row>
        <v-flex xs12>
          <dataset-table :search="search"></dataset-table>
        </v-flex>
      </v-layout>
      <v-snackbar
        right
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
      </v-snackbar>
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

  data() {
    return {
      snackbar: false,
      createCohortSheet: false,
      addDataSheet: false,
      search: '',
    };
  },
  filters: {
    buildPath(datasets) {
      // This constructs the build path with selected dataset ids
      if (!datasets) return 'build';

      const idParams = datasets
        .map(dataset => dataset.id)
        .map(id => `id=${id}`)
        .join('&');

      return `build?${idParams}`;
    },
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
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
    intersection() {
      // Compute the intersection of outcome measures
      // between selected datasets
      if (!this.selectedDatasets) return [];
      if (this.selectedDatasets.length < 2); return [];

      const outcomeMeasures = this.selectedDatasets
        .map(({ outcomes }) => outcomes.children);
      return outcomeMeasures
        .reduce((a, b) => a.filter(c => b.includes(c)));
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

#foo {
/* background: rgb(3,120,200);
background: linear-gradient(260deg, rgba(3,120,200,1) 0%, rgba(3,155,229,1) 100%); */
background: rgb(3,140,207);
background: linear-gradient(260deg, rgba(3,140,207,1) 0%, rgba(3,155,229,1) 100%);
}
</style>
