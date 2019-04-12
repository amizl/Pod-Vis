<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Create Collection</v-toolbar-title>
    </v-toolbar>
    <v-layout row justify-center>
      <v-flex xs12>
        <!-- <p class="subheading grey--text ligthen-2">Selected Datasets:</p> -->
        <v-container grid-list-lg fluid pt-0 mt-0 pl-0 ml-0>
          <v-layout row wrap>
            <v-flex v-for="dataset in selectedDatasets" :key="dataset.id" xs4>
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
    <v-layout class="pt-2" row justify-center>
      <v-flex xs12>
        <v-card>
          <v-card-title card color="white">
            <span class="title">Common Variables</span>
          </v-card-title>
          <div v-if="variables.length">
            <variable-table :variables="variables" :histogram="false" />
          </div>
          <div v-else>
            <v-card-text>
              <loading-spinner medium class="ma-5"></loading-spinner>
            </v-card-text>
          </div>
        </v-card>
      </v-flex>
    </v-layout>
    <v-layout
      v-for="dataset in selectedDatasets"
      :key="dataset.id"
      class="pt-4"
      row
      justify-center
    >
      <v-flex xs12>
        <v-card>
          <v-card-title card color="white">
            <span class="title">{{ dataset.study_name }}</span>
          </v-card-title>
          <div v-if="true">
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
    id: {
      type: [String, Array],
      default: null,
    },
  },
  data() {
    return {
      variables: [],
      activeDataset: null,
    };
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
  async created() {
    // selectedDatasets.forEach(dataset => {
    //   this.dataset.id;
    // });
    const { data } = await this.fetchSharedVariables();
    this.variables = data.variables;
  },
  methods: {
    ...mapActions('datasetManager', {
      addSelectedDatasetsToCohorts: actions.ADD_SELECTED_DATASETS_TO_COHORTS,
    }),
    goBack() {
      this.$router.go(-1);
    },
    fetchDemographicSummary(id) {
      // Forms a query similar to group_by=sex&group_by=race
      const groupBy = ['sex', 'race'];
      const queryParams = groupBy.map(group => `group_by=${group}`).join('&');

      return axios.get(`/api/studies/${id}/subjects/count?${queryParams}`);
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
