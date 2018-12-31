<template>
  <div>
    <v-toolbar app class="white">
      <v-toolbar-items>
        <v-btn flat @click="goBack">
          <v-icon left> arrow_back </v-icon>
          BACK TO DATASET MANAGER
        </v-btn>
      </v-toolbar-items>
      <v-spacer></v-spacer>
      <v-btn class="primary">
        <v-icon circle small color="iconColor" left> add </v-icon>
        ADD TO PROFILE
      </v-btn>
    </v-toolbar>
    <div class="white--text blueGradient">
      <v-container fluid>
        <v-layout row wrap>
          <v-flex xs6>
            <p class="headline font-weight-medium">{{ dataset.dataset }}</p>
          </v-flex>
          <!-- TODO: Info about selected here -->
          <v-flex xs6>
            <v-layout row>
              <v-flex xs6> </v-flex>
              <v-flex xs6> </v-flex>
            </v-layout>
          </v-flex>
        </v-layout>
      </v-container>
    </div>
    <v-container v-if="dataset" fluid grid-list-lg>
      <v-layout row wrap justify-center>
        <v-flex xs6>
          <v-card class="elevation-5">
            <v-toolbar card dense>
              <v-toolbar-title> About </v-toolbar-title>
            </v-toolbar>
            <div class="ma-2">
              <!-- <v-card-title
                primary-title
              >
                <h3>
                  {{ dataset.dataset }}
                </h3>
              </v-card-title> -->
              <v-card-text>
                <p>{{ dataset.description }}</p>
              </v-card-text>
              <v-card-actions v-if="dataset.sourceURL">
                <v-spacer></v-spacer>
                <v-btn :href="dataset.sourceURL" flat>Link to Study</v-btn>
              </v-card-actions>
            </div>
          </v-card>
        </v-flex>
        <v-flex xs6>
          <v-card class="elevation-5">
            <v-toolbar card dense>
              <v-toolbar-title> Subject Summary </v-toolbar-title>
            </v-toolbar>
            <!-- <v-card-title>DONUT CHART HERE</v-card-title> -->
            <v-card-text>
              <sunburst-chart
                v-if="dataset.cohort_summary"
                :data="JSON.parse(dataset.cohort_summary)"
              >
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
          </v-card>
        </v-flex>
      </v-layout>
      <v-layout row wrap justify-center>
        <v-flex xs6>
          <v-card class="elevation-5">
            <v-toolbar card dense>
              <v-toolbar-title> Outcome Categories </v-toolbar-title>
            </v-toolbar>
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
          <v-card class="elevation-5">
            <v-toolbar card dense>
              <v-toolbar-title> Demographics </v-toolbar-title>
            </v-toolbar>
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
      <v-layout row wrap justify-center>
        <v-flex xs12>
          <v-card class="elevation-5">
            <v-toolbar card dense>
              <v-toolbar-title> Variables </v-toolbar-title>
            </v-toolbar>
            <variable-table
              v-if="dataset"
              :variables="dataset.variables"
            ></variable-table>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import * as firebase from 'firebase';
import VariableTable from '@/components/DatasetManager/VariableTable.vue';
// Import these into a Subject Summary Component?
import SunburstChart from '@/components/charts/sunburst/SunburstChart.vue';
import SunburstLegend from '@/components/charts/sunburst/SunburstLegend.vue';

export default {
  components: {
    VariableTable,
    SunburstChart,
    SunburstLegend,
  },
  props: {
    id: String,
  },
  data() {
    return {
      dataset: null,
    };
  },
  computed: {
    ...mapState('datasetManager', {
      loading: state.IS_LOADING,
      datasets: state.DATASETS,
    }),
  },
  async created() {
    const dataset = await this.fetchDataset(this.id);
    if (dataset.exists) {
      this.dataset = dataset.data();
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    fetchDataset() {
      return firebase
        .firestore()
        .collection('datasets')
        .doc(this.id)
        .get();
    },
  },
};
</script>

<style scoped></style>
