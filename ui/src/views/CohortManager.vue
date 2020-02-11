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
        <v-flex xs12 sm12>
          <CohortSelection class="mt-2" @selectedCohort="cohortLoaded" />
        </v-flex>
      </v-toolbar-items>
      <v-spacer></v-spacer>

      <delete-cohort-button />
      <save-cohort-button @cohortSaved="cohortLoaded" />

      <v-tooltip top color="primary">
        <template v-slot:activator="{ on }">
          <analysis-summary-button :collection-id="collectionId" />
        </template>
        <span>View Analysis Summary for all Cohorts and Outcome Variables</span>
      </v-tooltip>
    </v-toolbar>

    <v-layout row class="ma-0 pa-0">
      <v-flex xs12>
        <analysis-tracker
          step="3"
          :substep.sync="substep"
          :collection-id="collectionId"
        ></analysis-tracker>
      </v-flex>
    </v-layout>

    <v-layout row fill-height class="mt-2 pa-0">
      <v-flex xs12>
        <input-variables
          :expanded.sync="inExpanded"
          :highlighted="inHighlighted"
        />
      </v-flex>
    </v-layout>

    <v-layout row class="mt-2 pa-0">
      <v-flex xs12>
        <output-variables
          :expanded.sync="outExpanded"
          :highlighted="outHighlighted"
          :disabled="true"
        />
      </v-flex>
    </v-layout>

    <v-layout row class="mt-2 pa-0">
      <v-flex xs6> <analytics-table :disabled="true" /> </v-flex>
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
import AnalysisSummaryButton from '@/components/DataExplorer/AnalysisSummaryBtnDialog';

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
    AnalysisSummaryButton,
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
      inExpanded: true,
      outExpanded: false,
      inHighlighted: true,
      outHighlighted: false,
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
  watch: {
    substep() {
      if (this.substep === '3.1') {
        this.inExpanded = true;
        this.outExpanded = false;
        this.inHighlighted = true;
        this.outHighlighted = false;
      } else if (this.substep === '3.2') {
        this.inExpanded = false;
        this.outExpanded = true;
        this.inHighlighted = false;
        this.outHighlighted = true;
      } else if (this.substep === '3.3') {
        this.inExpanded = true;
        this.outExpanded = true;
        this.inHighlighted = true;
        this.outHighlighted = false;
      } else if (this.substep === '3.4') {
        this.inHighlighted = false;
        this.outHighlighted = false;
      }
    },
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
    cohortSaved(success) {
      // go back to first substep
//      if (success) {
//        this.substep = '3.1';
//      }
    },
    cohortLoaded(newCohort) {
      if (newCohort.label !== 'New Cohort') {
        this.substep = '3.5';
      } else {
        this.substep = '3.1';
      }
    },
  },
};
</script>

<style scoped></style>
