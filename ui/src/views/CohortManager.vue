<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <loading-spinner />
  </v-container>
  <v-container v-else fluid fill-width class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Cohort Manager
        <div class="subheading">Dataset: {{ collection.label }}</div>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-flex xs12 sm12>
          <CohortSelection class="mt-2" @selectedCohort="cohortLoaded" />
        </v-flex>
      </v-toolbar-items>
      <v-spacer></v-spacer>

      <delete-cohort-button @cohortDeleted="cohortDeleted" />
      <save-cohort-button
        :cohorts="this.collection_cohorts"
        @cohortSaved="cohortSaved"
      />

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
          @createSimilar="createSimilar"
          @createNew="createNew"
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
      <v-flex xs7>
        <output-variables
          :expanded.sync="outExpanded"
          :highlighted="outHighlighted"
          :disabled="true"
        />
      </v-flex>
      <v-flex class="ml-2" xs5> <analytics-table /> </v-flex>
    </v-layout>

    <v-layout v-if="false" row class="mt-2 pa-0">
      <v-flex xs6> <cohort-table /> </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState, mapGetters } from 'vuex';
import { actions, state, getters } from '@/store/modules/cohortManager/types';

import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import CohortSelection from '@/components/CohortManager/CohortSelection.vue';
import CohortTable from '@/components/CohortManager/CohortTable.vue';
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
    CohortTable,
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
      cohorts: state.COHORTS,
    }),
    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;

      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          cch.push(e);
        }
      });

      return cch;
    },
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
      setCohort: actions.SET_COHORT,
    }),
    cohortSaved(success) {
      this.substep = '3.5';
    },
    // create entirely new cohort resetting everything
    createNew(success) {
      // return to "choose predictor variables" step
      this.setCohort({ id: null });
      this.substep = '3.1';
    },
    // create new cohort similar to the most-recently-created one
    createSimilar(success) {
      var ncc = this.collection_cohorts.length;
      // load last cohort in the list
      if (ncc > 0) {
        var last_cohort = this.collection_cohorts[ncc - 1];
        this.setCohort(last_cohort);
      }
      // return to "add filters" step
      this.substep = '3.3';
    },
    cohortLoaded(newCohort) {
      if (
        newCohort.label !== 'New Cohort' &&
        newCohort.label !== 'Choose Cohort'
      ) {
        this.substep = '3.3';
      } else {
        this.substep = '3.1';
      }
    },
    cohortDeleted() {
      this.substep = '3.1';
    },
  },
};
</script>

<style scoped></style>
