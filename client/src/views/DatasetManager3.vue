<template>
  <v-container
    fluid
    fill-height
    grid-list-xl
  >
    <!-- <v-toolbar
      app
      class="primary"
    >
    </v-toolbar> -->
    <v-layout justify-center>
      <v-flex xs10>
        <build-dataset-stepper></build-dataset-stepper>
      </v-flex>
    </v-layout>
  </v-container>
</template>
<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
//  import Header from '@/components/layout/Header.vue';
// import DatasetTable from '@/components/DatasetManager/DatasetTable.vue';
// import OutcomeTable from '@/components/DatasetManager/OutcomeTable.vue';
// import DemographicsTable from '@/components/DatasetManager/DemographicsTable.vue';
// import FilterTree from '@/components/DatasetManager/FilterTree.vue';
import BuildDatasetStepper from '@/components/DatasetManager/BuildDatasetStepper.vue';
//  import DonutChart from '@/components/charts/DonutChart.vue';

export default {
  components: {
    // datasetTable: DatasetTable,
    // donutChart: DonutChart,
    // contentHeader: Header,
    // filterTree: FilterTree,
    // OutcomeTable,
    // DemographicsTable,
    BuildDatasetStepper,
  },
  data() {
    return {
    };
  },
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
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
