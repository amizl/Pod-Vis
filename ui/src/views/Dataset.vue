<template>
  <div>
    <v-container v-if="dataset" fluid grid-list-xl>
      <v-toolbar app class="primary">
        <v-toolbar-title class="white--text">Dataset Overview</v-toolbar-title>
      </v-toolbar>
      <v-layout row wrap justify-center>
        <v-flex xs8>
          <v-layout row wrap justify-center>
            <v-flex xs12>
              <v-card flat class="rounded-lg shadow">
                <v-card-title primary-title card color="white">
                  <p class="title mb-0 ">
                    {{ dataset.study.study_name }} <br />
                    <span class="caption grey--text lighten-2">
                      {{ dataset.study.project.project_name }}
                    </span>
                  </p>
                </v-card-title>
                <v-card-text>
                  <p>{{ dataset.study.description }}</p>
                </v-card-text>
                <v-card-actions v-if="dataset.sourceURL">
                  <v-spacer></v-spacer>
                  <v-btn :href="dataset.sourceURL" flat>Link to Study</v-btn>
                </v-card-actions>
              </v-card>
            </v-flex>
          </v-layout>
          <v-layout row wrap justify-center>
            <v-flex xs12>
              <v-card flat class="rounded-lg shadow">
                <v-card-title primary-title card color="white">
                  <span class="title">Variables</span>
                </v-card-title>
                <variable-table :dataset-id="id" />
              </v-card>
            </v-flex>
          </v-layout>
        </v-flex>
        <v-flex xs4>
          <v-card flat class="rounded-lg shadow">
            <v-card-title primary-title card color="white">
              <span class="title">Subject Summary</span>
            </v-card-title>
            <v-card-text v-if="summaryData">
              <sunburst-chart
                :data="summaryData"
                :keyorder="groupBy"
                :color="{ male: '#3498DB', female: '#FFC0CB' }"
              >
                <template
                  v-slot:legend="{ data, color, colorScale, actions, nodes }"
                >
                  <sunburst-legend
                    :data="data"
                    :color-scale="colorScale"
                    :color="color"
                    :actions="actions"
                    :nodes="nodes"
                  ></sunburst-legend>
                </template>
              </sunburst-chart>
            </v-card-text>
            <v-card-text v-else>
              <loading-spinner medium class="ma-5" />
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
    <!-- SNACKBARS -->
    <v-snackbar v-model="addToProfileSuccess" color="success" top>
      Dataset was successfully added to your profile.
    </v-snackbar>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import axios from 'axios';
import VariableTable from '@/components/DatasetManager/VariableTable.vue';
// Import these into a Subject Summary Component?
import SunburstChart from '@/components/charts/sunburst/SunburstChart.vue';
import SunburstLegend from '@/components/charts/sunburst/SunburstLegend.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';

export default {
  components: {
    VariableTable,
    SunburstChart,
    SunburstLegend,
    LoadingSpinner,
  },
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      dataset: null,
      addToProfileSuccess: false,
      summaryData: null,
      groupBy: ['Sex', 'Race'],
    };
  },
  computed: {
    ...mapState('datasetManager', {
      loading: state.IS_LOADING,
      datasets: state.DATASETS,
    }),
  },
  async created() {
    const { data: dataset } = await this.fetchDataset();
    if (dataset) {
      this.dataset = dataset;

      this.fetchDemographicSummary().then(({ data }) => {
        const { counts } = data;
        this.summaryData = counts;
      });
    }
  },
  methods: {
    ...mapActions('dashboard', {
      _addToProfile: actions.ADD_DATASET_TO_PROFILE,
    }),
    addToProfile() {
      const payload = {
        dataset: this.dataset.dataset,
        id: this.id,
      };
      this._addToProfile(payload).then(() => (this.addToProfileSuccess = true));
    },
    goBack() {
      this.$router.go(-1);
    },
    fetchDataset() {
      return axios.get(`/api/studies/${this.id}?include=project`);
    },
    fetchDemographicSummary() {
      // Forms a query similar to group_by=sex&group_by=race
      const queryParams = this.groupBy
        .map(group => `group_by=${group}`)
        .join('&');

      return axios.get(`/api/studies/${this.id}/subjects/count?${queryParams}`);
    },
  },
};
</script>

<style scoped></style>
