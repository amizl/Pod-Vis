<template>
  <div>
    <v-container v-if="dataset" fluid grid-list-xl>
      <v-toolbar app class="white">
        <v-toolbar-title>Dataset Overview</v-toolbar-title>
      </v-toolbar>
      <v-layout row wrap justify-center>
        <v-flex xs8>
          <v-layout row wrap justify-center>
            <v-flex xs12>
              <v-card>
                <v-card-title primary-title card color="white">
                  <p class="title mb-0 ">
                    {{ dataset.study.study_name }} <br />
                    <span class="caption grey--text lighten-2">
                      {{ dataset.study.project.project_name }}
                    </span>
                  </p>
                </v-card-title>
                <v-card-text>
                  <p>{{ descriptions[dataset.study.study_name] }}</p>
                </v-card-text>
                <v-card-actions v-if="dataset.sourceURL">
                  <v-spacer></v-spacer>
                  <v-btn :href="dataset.sourceURL" flat>Link to Study</v-btn>
                </v-card-actions>
              </v-card>
            </v-flex>
          </v-layout>
          <v-layout row wrap justify-center>
            <!-- <v-flex xs2>
          <v-card>
            <v-card-title primary-title card color="white">
              <span class="title">
                <v-icon>settings</v-icon> Filter Variables</span
              >
            </v-card-title>
            <v-treeview :items="items"></v-treeview>
          </v-card>
        </v-flex> -->
            <v-flex xs12>
              <v-card>
                <v-card-title primary-title card color="white">
                  <span class="title">Variables</span>
                </v-card-title>
                <variable-table :dataset-id="id" />
              </v-card>
            </v-flex>
          </v-layout>
        </v-flex>
        <v-flex xs4>
          <v-card>
            <v-card-title primary-title card color="white">
              <span class="title">Subject Summary</span>
            </v-card-title>
            <v-card-text v-if="summaryData">
              <sunburst-chart :data="summaryData" :keyorder="groupBy">
                <sunburst-legend
                  slot="legend"
                  slot-scope="{ data, color, actions, nodes }"
                  :data="data"
                  :color="color"
                  :actions="actions"
                  :nodes="nodes"
                ></sunburst-legend>
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
      type: String,
      default: '',
    },
  },
  data() {
    return {
      dataset: null,
      items: [
        {
          id: 1,
          name: 'Category',
          children: [
            { id: 2, name: 'Calendar : app' },
            { id: 3, name: 'Chrome : app' },
            { id: 4, name: 'Webstorm : app' },
          ],
        },
      ],
      addToProfileSuccess: false,
      summaryData: null,
      variables: [],
      groupBy: ['sex', 'race'],
      // TODO: Descriptions need to be loaded into database
      descriptions: {
        "Parkinson's Disease":
          'Subjects with a diagnosis of PD for two years or less who are not taking PD medications.',
        'Healthy Control':
          'Control Subjects without PD who are 30 years or older and who do not have a first degree blood relative with PD.',
        SWEDD:
          'Subjects consented as PD subjects who have DaTscans that do not show evidence of a dopaminergic deficit.',
        Prodomal:
          "Subjects without Parkinson's disease who have a diagnosis of hyposmia or REM sleep behavior disorder (RBD).",
        'Genetic Cohort PD':
          "Subjects with Parkinson's disease who have a genetic mutation in LRRK2, GBA, or SNCA.",
        'Genetic Cohort Unaffected':
          "Subjects without Parkinson's disease who have a genetic mutation in LRRK2, GBA, or SNCA.",
        'Genetic Registry PD':
          "Subjects with Parkinson's disease who have a genetic mutation in LRRK2, GBA, or SNCA or a first-degree relative with a LRRK2, GBA, or SNCA mutation who are evaluated at less frequent intervals to augment and broaden the follow-up of PD subjects and family members with PD associated mutations.",
        'Genetic Registry Unaffected':
          "Subjects without Parkinson's disease who have a genetic mutation in LRRK2, GBA, or SNCA or a first-degree relative with a LRRK2, GBA, or SNCA mutation who are evaluated at less frequent intervals to augment and broaden the follow-up of PD subjects and family members with PD associated mutations.",
      },
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

      this.fetchVariables().then(({ data }) => {
        this.variables = data.variables;
      });

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
    fetchVariables() {
      return axios.get(`/api/studies/${this.id}/variables`);
    },
  },
};
</script>

<style scoped></style>
