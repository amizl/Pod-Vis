<template>
  <div>
    <v-toolbar class="background" flat app extended>
      <p class="mt-5 ml-5 display-1 foo--text">Dashboard</p>
    </v-toolbar>
    <!-- <div class="white--text blueGradient">
      <v-container fluid>
        <v-layout row wrap>
          <v-flex xs6>
            <p class="headline font-weight-medium">Dashboard</p>
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
    <v-container grid-list-md fluid>
      <!-- <loading-spinner v-if="isLoading"></loading-spinner> -->
      <!-- <v-layout justify-space-around>
        <v-flex xs8>
          <p class="headline primary--text">Recent Datasets</p>
          <v-layout>
            <v-flex xs6>
              <v-card flat class="ui-card">
                <v-card-title></v-card-title>
                <v-card-text>
                  <p class="subheading">
                    University of Maryland Parkinson's Disease & Movement
                    Disorders Center HOME Study
                  </p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn flat small>Analyze</v-btn>
                  <v-btn flat small>Create Cohort</v-btn>
                </v-card-actions>
              </v-card>
            </v-flex>
            <v-flex xs6>
              <v-card flat class="ui-card">
                <v-card-title></v-card-title>
                <v-card-text>
                  <p class="subheading">
                    Parkinson's Progression Marker Initiative
                  </p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn flat small>Analyze</v-btn>
                  <v-btn flat small>Create Cohort</v-btn>
                </v-card-actions>
              </v-card>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout> -->
      <v-layout row justify-center class="mt-5">
        <v-flex xs8>
          <p class="subheading foo--text">My Datasets</p>
          <dataset-table></dataset-table>
          <!-- <v-card>
            <v-card-title></v-card-title>
            <v-card-text> </v-card-text>
          </v-card> -->
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dashboard/types';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import DatasetTable from '@/components/dashboard/DatasetTable.vue';

export default {
  components: {
    LoadingSpinner,
    DatasetTable,
  },
  computed: {
    ...mapState('dashboard', {
      datasets: state.DATASETS,
      isLoading: state.IS_LOADING,
    }),
  },
  created() {
    if (!this.datasets.length) {
      this.fetchDatasets();
    }
  },
  methods: {
    ...mapActions('dashboard', {
      fetchDatasets: actions.FETCH_DATASETS,
    }),
  },
};
</script>

<style scoped></style>
