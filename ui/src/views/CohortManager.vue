<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0"> <loading-spinner /> </v-col>
    </v-row>
  </v-container>

  <v-container v-else fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>group_add</v-icon>
      <v-toolbar-title class="white--text pl-3"
        >Cohort Manager
        <div class="subtitle-1">
          Dataset:
          <v-tooltip bottom color="primary">
            <template v-slot:activator="{ on: tooltip }">
              <span v-on="{ ...tooltip }">{{ collection.label }}</span>
            </template>
            <span class="subtitle-1">{{
              getCollectionDescription(collection)
            }}</span>
          </v-tooltip>
        </div>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <CohortSelection class="mt-2" @selectedCohort="cohortSelected" />
      </v-toolbar-items>

      <v-spacer></v-spacer>

      <delete-cohort-button class="mx-1" @cohortDeleted="cohortDeleted" />
      <save-cohort-button
        :cohorts="this.collection_cohorts"
        class="mx-1"
        @cohortSaved="cohortSaved"
      />

      <v-tooltip top color="primary">
        <template v-slot:activator="{ on: tooltip }">
          <analysis-summary-button
            :collection-id="collectionId"
            class="mx-1"
            v-on="{ ...tooltip }"
          />
        </template>
        <span>View Analysis Summary for all Cohorts and Outcome Variables</span>
      </v-tooltip>
    </v-app-bar>

    <v-container
      v-if="!collection.has_visits_set"
      fluid
      fill-height
      class="ma-0 pa-0"
    >
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-sheet color="white" height="100%" class="rounded-lg shadow">
            <span
              >ERROR - First/Last Visits must be set in order to use the Cohort
              Manager:<br clear="both"
            /></span>
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on }">
                <v-btn
                  width="15em"
                  @click="
                    $router.push(`data_summary?collection=${collection.id}`)
                  "
                  v-on="on"
                >
                  Set Visits
                </v-btn>
              </template>
              <span class="subtitle-1"
                >View Data Summary and choose First &amp; Last Visit</span
              >
            </v-tooltip>
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>

    <div v-else fill-width class="ma-0 pa-0">
      <analysis-tracker
        step="3"
        :substep.sync="substep"
        :collection-id="collectionId"
        @createSimilar="createSimilar"
        @createNew="createNew"
      ></analysis-tracker>

      <v-container fluid fill-width class="ma-0 pa-0 pt-2">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-sheet
              color="white"
              height="100%"
              class="rounded-lg shadow pa-0 ma-0"
            >
              <input-variables
                :expanded.sync="inExpanded"
                :highlighted="inHighlighted"
                class="ma-0 pt-0"
                @userSelectedInputVariables="userSelectedVariables"
                @userChangedInputVariable="userChangedVariable"
              />
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>

      <v-container fluid fill-width class="ma-0 pa-0 pt-2">
        <v-row class="ma-0 pa-0">
          <v-col cols="7" class="ma-0 pa-0">
            <output-variables
              :expanded.sync="outExpanded"
              :highlighted="outHighlighted"
              :disabled="true"
              class="ma-0 pt-0"
              @userSelectedOutputVariables="userSelectedVariables"
              @userChangedOutputVariable="userChangedVariable"
            />
          </v-col>
          <v-col cols="5" class="ma-0 pa-0">
            <analytics-table class="ml-2" />
          </v-col>
        </v-row>
      </v-container>
    </div>
  </v-container>
</template>

<script>
import { mapActions, mapState, mapGetters } from 'vuex';
import { actions, state, getters } from '@/store/modules/cohortManager/types';
import {
  getCollectionDescription,
  getLongScaleNameDefault,
} from '@/utils/helpers';

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
      isLoadingCohort: false,
      substep: '3.1',
      inExpanded: true,
      outExpanded: false,
      inHighlighted: true,
      outHighlighted: false,
      getCollectionDescription: getCollectionDescription,
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
    var datasets = this.collection.studies.map(d => d.study);
    var useLongScaleNames = getLongScaleNameDefault(datasets);
    this.setUseLongScaleNames(useLongScaleNames);
    this.isLoading = false;
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchData: actions.FETCH_DATA,
      resetAllStoreData: actions.RESET_ALL_STORE_DATA,
      setCohort: actions.SET_COHORT,
      setCohortNoReset: actions.SET_COHORT_NO_RESET,
      setUseLongScaleNames: actions.SET_USE_LONG_SCALE_NAMES,
    }),
    userSelectedVariables() {
      this.setCohortNoReset({ id: -1 });
    },
    userChangedVariable() {
      this.setCohortNoReset({ id: -1 });
    },
    cohortSaved(success) {
      this.substep = '3.5';
    },
    // create entirely new cohort resetting everything
    createNew(success) {
      // return to "choose predictor variables" step
      this.setNewCohort({ id: null });
      this.substep = '3.1';
    },
    // create new cohort similar to the most-recently-created one
    createSimilar(success) {
      var ncc = this.collection_cohorts.length;
      // load last cohort in the list
      if (ncc > 0) {
        var last_cohort = this.collection_cohorts[ncc - 1];
        this.setNewCohort(last_cohort);
      }
      // return to "add filters" step
      this.substep = '3.3';
    },
    cohortSelected(newCohort) {
      this.setNewCohort(newCohort);
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
    async setNewCohort(newCohort) {
      if (this.isLoadingCohort) {
        console.log(
          'WARNING - setNewCohort called when cohort load in progress'
        );
      }
      this.isLoadingCohort = true;
      await this.setCohort(newCohort);
      this.isLoadingCohort = false;
    },
  },
};
</script>

<style scoped></style>
