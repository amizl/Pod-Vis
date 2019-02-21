<template>
  <div>
    <v-toolbar app class="white">
      <v-toolbar-items>
        <v-btn flat @click="goBack">
          <v-icon left> arrow_back </v-icon>
          BACK TO DATASET MANAGER
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <div class="primary white--text blueGradient">
      <v-container fluid>
        <v-layout row wrap>
          <v-flex xs6>
            <p class="headline font-weight-medium">Build Dataset</p>
            <!-- <v-chip
              close
              v-for='{ id, code } in selectedDatasets'
              :key='id'>
              {{ code }}
            </v-chip> -->
          </v-flex>
          <!-- TODO: Info about selected here -->
          <v-spacer></v-spacer>
          <v-flex xs6 class="text-xs-right">
            <p class="subheading">SELECTED DATASETS</p>
            <v-chip v-for="{ id, code } in selectedDatasets" :key="id" close>
              {{ code }}
            </v-chip>
            <!-- <v-layout row>
              <v-flex xs6>
              </v-flex>
              <v-flex xs6>
              </v-flex>
            </v-layout> -->
          </v-flex>
        </v-layout>
      </v-container>
    </div>
    <v-container fluid fill-height grid-list-xl>
      <v-layout justify-center>
        <v-flex xs12>
          <build-dataset-stepper
            :outcome-measures="outcomeMeasures"
          ></build-dataset-stepper>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
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
  props: {
    // id is passed in via route parameters
    // i.e., /build?id=x&id=y
    id: [String, Array],
  },
  data() {
    return {};
  },
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
    outcomeMeasures() {
      return this.selectedDatasets
        ? this.selectedDatasets
            .map(dataset =>
              dataset.outcomes.map(outcome => ({
                name: outcome.category,
                dataset: dataset.code,
                outcomeMeasures: outcome.children.map(name => ({
                  name,
                  dataset: dataset.code,
                })),
              }))
            )
            .flat()
        : [];
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

<style scoped></style>
