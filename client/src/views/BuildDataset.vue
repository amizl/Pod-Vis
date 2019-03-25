<template>
  <!-- <div>
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
  <!-- </v-flex> -->
  <!-- TODO: Info about selected here -->
  <!-- <v-spacer></v-spacer> -->
  <!-- <v-flex xs6 class="text-xs-right">
            <p class="subheading">SELECTED DATASETS</p>
            <v-chip v-for="{ id, code } in selectedDatasets" :key="id" close>
              {{ code }}
            </v-chip>
            <!-- <v-layout row> -->
  <!-- <v-flex xs6>
              </v-flex>
              <v-flex xs6>
              </v-flex>
            </v-layout> -->
  <!-- </v-flex>
        </v-layout>
      </v-container>
    </div> -->
  <v-container fluid>
    <v-layout class="mt-4" justify-center>
      <v-flex xs10>
        <v-layout>
          <v-flex xs6> <p class="headline">Create Collection</p> </v-flex>
          <v-flex xs6> <!-- OTHER ACTION ITES HERE --> </v-flex>
        </v-layout>
        <v-divider></v-divider>
        <!-- <build-dataset-stepper
            :outcome-measures="outcomeMeasures"
          ></build-dataset-stepper> -->
      </v-flex>
    </v-layout>
    <v-layout class="pt-5" row justify-center>
      <v-flex xs10>
        <p class="subheading grey--text ligthen-2">Selected Datasets:</p>
        <v-container grid-list-lg fluid pt-0 mt-0>
          <v-layout row wrap>
            <v-flex v-for="dataset in selectedDatasets" :key="dataset.id" xs3>
              <v-card>
                <v-card-title primary-title>
                  <div>
                    <div class="subheading">{{ dataset.study_name }}</div>
                    <span class="caption grey--text lighten-2">{{
                      dataset.project_name
                    }}</span>
                  </div>
                </v-card-title>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn :to="`/datasets/${dataset.id}`" flat icon>
                    <v-tooltip top color="primary">
                      <v-icon slot="activator"> info </v-icon>
                      <span>Learn more about this study</span>
                    </v-tooltip>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-flex>
          </v-layout>
        </v-container>
      </v-flex>
    </v-layout>
    <v-layout class="pt-4" row justify-center>
      <v-flex xs10>
        <p class="subheading grey--text ligthen-2">
          Shared Variables in Selected Datasets:
        </p>
        <v-card>
          <!-- <v-card-title card color="white">
            <span class="title">Variables</span>
          </v-card-title> -->
          <div v-if="variables.length !== 0">
            <variable-table :variables="variables" :histogram="false" />
          </div>
          <div v-else>
            <v-card-text> <loading-spinner medium class="ma-5" /> </v-card-text>
          </div>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import axios from 'axios';
//  import Header from '@/components/layout/Header.vue';
// import DatasetTable from '@/components/DatasetManager/DatasetTable.vue';
// import OutcomeTable from '@/components/DatasetManager/OutcomeTable.vue';
// import DemographicsTable from '@/components/DatasetManager/DemographicsTable.vue';
// import FilterTree from '@/components/DatasetManager/FilterTree.vue';
import BuildDatasetStepper from '@/components/DatasetManager/BuildDatasetStepper.vue';
//  import DonutChart from '@/components/charts/DonutChart.vue';
import VariableTable from '@/components/DatasetManager/VariableTable.vue';

export default {
  components: {
    // datasetTable: DatasetTable,
    // donutChart: DonutChart,
    // contentHeader: Header,
    // filterTree: FilterTree,
    // OutcomeTable,
    // DemographicsTable,
    BuildDatasetStepper,
    VariableTable,
  },
  props: {
    // id is passed in via route parameters
    // i.e., /build?id=x&id=y
    id: [String, Array],
  },
  data() {
    return {
      variables: [],
    };
  },
  async created() {
    const { data } = await this.fetchSharedVariables();
    this.variables = data.variables;
  },
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
    // outcomeMeasures() {
    //   return this.selectedDatasets
    //     ? this.selectedDatasets
    //         .map(dataset =>
    //           dataset.outcomes.map(outcome => ({
    //             name: outcome.category,
    //             dataset: dataset.code,
    //             outcomeMeasures: outcome.children.map(name => ({
    //               name,
    //               dataset: dataset.code,
    //             })),
    //           }))
    //         )
    //         .flat()
    //     : [];
    // },
  },
  methods: {
    ...mapActions('datasetManager', {
      addSelectedDatasetsToCohorts: actions.ADD_SELECTED_DATASETS_TO_COHORTS,
    }),
    goBack() {
      this.$router.go(-1);
    },
    fetchSharedVariables() {
      const base = `/api/studies/variables`;
      const query = this.selectedDatasets
        .map(d => d.id)
        .map(id => `id=${id}`)
        .join('&');

      return axios.get(`${base}?${query}`);
    },
  },
};
</script>

<style scoped></style>
