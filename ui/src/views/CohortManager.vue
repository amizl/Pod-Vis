<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <loading-spinner />
  </v-container>
  <v-container v-else fluid fill-width class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Cohort Manager
        <div class="subheading">{{ collection.label }}</div>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-flex xs12 sm12> <CohortSelection class="mt-2" /> </v-flex>
      </v-toolbar-items>
      <v-spacer></v-spacer>

      <delete-cohort-button />
      <save-cohort-button />

      <v-tooltip top color="primary">
        <template v-slot:activator="{ on }">
          <data-explorer-button />
        </template>
        <span>Launch Data Explorer to compare Cohorts</span>
      </v-tooltip>
    </v-toolbar>

    <v-layout row class="ma-0 pa-0">
      <v-flex xs12>
        <analysis-tracker
          step="3"
          :substep="substep"
          :collection-id="collectionId"
        ></analysis-tracker>
      </v-flex>
    </v-layout>

    <v-layout row fill-height class="mt-2 pa-0">
      <v-flex xs12> <input-variables /> </v-flex>
    </v-layout>

    <v-layout row class="mt-2 pa-0">
      <v-flex xs12> <output-variables /> </v-flex>
    </v-layout>

    <v-layout row class="mt-2 pa-0">
      <v-flex xs6> <analytics-table /> </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState, mapGetters } from 'vuex';
import { actions, state, getters } from '@/store/modules/cohortManager/types';

import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import CohortSelection from '@/components/CohortManager/CohortSelection.vue';
import AnalyticsTable from '@/components/CohortManager/AnalyticsTable.vue';
import InputVariables from '@/components/CohortManager/InputVariables.vue';
import OutputVariables from '@/components/CohortManager/OutputVariables.vue';
import DeleteCohortButton from '@/components/CohortManager/DeleteCohortBtnDialog';
import SaveCohortButton from '@/components/CohortManager/SaveCohortBtnDialog';
import DataExplorerButton from '@/components/CohortManager/DataExplorerBtnDialog';

export default {
  name: 'CohortManager',
  components: {
    AnalysisTracker,
    CohortSelection,
    InputVariables,
    OutputVariables,
    AnalyticsTable,
    SaveCohortButton,
    DeleteCohortButton,
    DataExplorerButton,
  },
  props: {
    collectionId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
      substep: '3.1',
    };
  },
  computed: {
    ...mapGetters('cohortManager', {
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
    }),
  },
  async created() {
    this.resetAllStoreData();

    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    this.isLoading = false;
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchData: actions.FETCH_DATA,
      resetAllStoreData: actions.RESET_ALL_STORE_DATA,
    }),
  },
};
</script>

<style scoped></style>
