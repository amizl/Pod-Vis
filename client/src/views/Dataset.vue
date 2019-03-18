<template>
  <div>
    <!-- <v-toolbar app class="white">
      <v-toolbar-items>
        <v-btn flat @click="goBack">
          <v-icon left> arrow_back </v-icon>
          BACK TO DATASET MANAGER
        </v-btn>
      </v-toolbar-items>
      <v-spacer></v-spacer>
      <v-btn class="primary" @click="addToProfile">
        <v-icon circle small color="iconColor" left> add </v-icon>
        ADD TO PROFILE
      </v-btn>
    </v-toolbar> -->
    <!-- <div class="white--text blueGradient">
      <v-container fluid>
        <v-layout row wrap>
          <v-flex xs6>
            <p class="headline font-weight-medium">{{ dataset.dataset }}</p>
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
    <v-container v-if="dataset" fluid grid-list-xl>
      <v-layout class="mt-3" justify-center>
        <v-flex xs10>
          <p class="headline mb-0">{{ dataset.study.study_name }}</p>
          <p class="caption grey--text lighten-2">
            {{ dataset.study.project.project_name }}
          </p>
          <v-divider></v-divider>
        </v-flex>
      </v-layout>
      <v-layout class="mt-4" row wrap justify-center>
        <v-flex xs10>
          <v-layout row wrap justify-center>
            <v-flex xs6>
              <v-card>
                <v-card-title card color="white">
                  <span class="title">About</span>
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
            <v-flex xs6>
              <v-card>
                <v-card-title card color="white">
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
        </v-flex>
      </v-layout>
      <!-- <v-layout row wrap justify-center>
        <v-flex xs10>
          <v-layout row wrap justify-center>
            <v-flex xs6>
              <v-card>
                <v-card-title card color="white">
                  <span class="title">Outcome Categories</span>
                </v-card-title>
                <v-card-text>
                  <v-chip
                    v-for="outcome in dataset.outcomes"
                    :key="outcome.category"
                  >
                    {{ outcome.category }}
                  </v-chip>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex xs6>
              <v-card class="ui-card">
                <v-card-title card color="white">
                  <span class="title">Demographics</span>
                </v-card-title>
                <v-card-text>
                  <v-chip
                    v-for="demographic in dataset.demographics"
                    :key="demographic.name"
                  >
                    {{ demographic.name }}
                  </v-chip>
                </v-card-text>
              </v-card>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>-->
      <v-layout row wrap justify-center>
        <v-flex xs10>
          <v-card>
            <v-card-title card color="white">
              <span class="title">Variables</span>
            </v-card-title>
            <variable-table
              v-if="dataset"
              :variables="dataset.variables"
            ></variable-table>
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
      addToProfileSuccess: false,
      summaryData: null,
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
    const { data } = await this.fetchDataset();
    if (data) {
      this.dataset = data;

      // Get demographics summary data for sunburst chart
      const summary = await this.fetchDemographicSummary();
      const { counts } = summary.data;
      this.summaryData = counts;
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
      const queryParams = this.groupBy
        .map(group => `group_by=${group}`)
        .join('&');

      return axios.get(`/api/studies/${this.id}/subjects/count?${queryParams}`);
    },
  },
};
</script>

<style scoped></style>
