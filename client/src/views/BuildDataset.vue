<template>
  <v-container
    fluid
    fill-height
    grid-list-xl
  >
    <v-toolbar
      app
      class='white'
    >
      <v-toolbar-items>
        <v-btn
          flat
          @click='goBack'
        >
          <v-icon left>
            arrow_back
          </v-icon>
          BACK TO DATASET MANAGER
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <v-layout justify-center>
      <v-flex xs12>
        <build-dataset-stepper
          :outcomeMeasures='outcomeMeasures'
        ></build-dataset-stepper>
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
  props: {
    // id is passed in via route parameters
    // i.e., /build?id=x&id=y
    id: [String, Array],
  },
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
      return this.selectedDatasets ? this.selectedDatasets
        .map(dataset => dataset.outcomes
          .map(outcome => ({
            name: outcome.category,
            dataset: dataset.code,
            outcomeMeasures: outcome.children.map(name => ({
                name,
                dataset: dataset.code,
              })
            ),
          })))
        .flat() : [];
    },
  },
  methods: {
    ...mapActions('datasetManager', {
      addSelectedDatasetsToCohorts: actions.ADD_SELECTED_DATASETS_TO_COHORTS,
    }),
    goBack() {
      this.$router.go(-1);
    },
  },
};
</script>

<style scoped>

</style>
