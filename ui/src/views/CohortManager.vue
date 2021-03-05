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

          <span class="ml-3">
            Selected Cohort:
            <v-tooltip bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span v-on="{ ...tooltip }">{{
                  cohort == null ? 'none' : cohort.label
                }}</span>
              </template>
              <span class="subtitle-1">{{
                cohort == null ? 'none' : cohort.query_string
              }}</span>
            </v-tooltip>
          </span>
        </div>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <v-tooltip bottom color="primary">
        <template v-slot:activator="{ on: tooltip }">
          <v-toolbar-items v-on="{ ...tooltip }">
            <v-checkbox
              v-model="helpModeCheckbox"
              dark
              class="mt-5"
            ></v-checkbox>
            <span class="white--text font-weight-bold mt-5">Help Mode</span>
          </v-toolbar-items>
        </template>
        <span class="subtitle-1">
          {{ helpMode ? 'Disable' : 'Enable' }} help mode.
        </span>
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

    <div v-else fill-width class="ma-0 pa-0" style="border 3px dotted green;">
      <analysis-tracker
        step="2"
        :substep.sync="substep"
        :collection-id="collectionId"
        @createSimilar="createSimilar"
        @createNew="createNew"
      ></analysis-tracker>

      <v-card :class="allPanelsClass">
        <v-container fluid fill-width class="pa-0 ma-0">
          <v-row class="ma-0 pa-0">
            <v-col cols="12" class="ma-0 pa-0">
              <splitpanes class="default-theme">
                <pane size="65" :style="inputVarsStyle" class="pb-1">
                  <v-sheet
                    color="white"
                    height="100%"
                    class="rounded-lg shadow pa-0 ma-0 mr-1"
                  >
                    <input-variables
                      :expanded.sync="inExpanded"
                      :highlighted="inHighlighted"
                      :class="inputVarsClass"
                      :show-add-help="helpMode && substep == '2.1'"
                      :show-filter-help="helpMode && substep == '2.3'"
                      @userSelectedInputVariables="userSelectedVariables"
                      @userChangedInputVariable="userChangedVariable"
                      @comparePredefinedRanges="comparePredefinedRanges"
                      @savePredefinedRanges="savePredefinedRanges"
                    >
                    </input-variables>
                  </v-sheet>
                </pane>

                <pane
                  min-size="25"
                  max-size="75"
                  size="35"
                  :style="manageCohortsStyle"
                  class="pb-1"
                >
                  <manage-cohorts-table
                    class="ml-1"
                    :cohorts="collection_cohorts"
                    :collection-id="collectionId"
                    :show-new-help="helpMode && substep == '2.2'"
                    :show-save-help="helpMode && substep == '2.4'"
                    :show-next-help="helpMode && collection_cohorts.length >= 2"
                    @selectedCohort="cohortSelected"
                    @newCohort="newCohort"
                  />
                </pane>
              </splitpanes>
            </v-col>
          </v-row>
        </v-container>

        <v-container fluid fill-width class="ma-0 pa-0 pt-1">
          <v-row class="ma-0 pa-0">
            <v-col cols="12" class="ma-0 pa-0">
              <splitpanes class="default-theme">
                <pane size="65" :style="outputVarsStyle">
                  <output-variables
                    :expanded.sync="outExpanded"
                    :highlighted="outHighlighted"
                    :disabled="true"
                    :class="outputVarsClass"
                    :show-add-help="helpMode && substep == 2.2"
                    :show-review-help="helpMode && substep == 2.4"
                    @userSelectedOutputVariables="userSelectedVariables"
                    @userChangedOutputVariable="userChangedVariable"
                  />
                </pane>

                <pane
                  min-size="25"
                  max-size="75"
                  size="35"
                  :style="analyticsTableStyle"
                >
                  <analytics-table class="ml-1" color-scheme="brewer5" />
                </pane>
              </splitpanes>
            </v-col>
          </v-row>

          <v-overlay absolute :value="helpMode && substep != 2.4"> </v-overlay>
        </v-container>
      </v-card>
    </div>
    <analytics-popup
      ref="apop"
      color-scheme="brewer5"
      :name="analyticsPopupName"
      :cohorts="analyticsPopupCohorts"
      :select-range-fn="analyticsPopupSelectRangeFn"
      :cohort-prefix="analyticsPopupCohortPrefix"
    />
    <v-snackbar
      v-model="helpModeNotify"
      color="#2a96f3"
      bottom
      multi-line
      class="pb-5"
    >
      <v-icon class="mr-2">help_outline</v-icon>
      <span class="font-weight-bold white--text subtitle-1">
        Toggle the help mode at any time by using the checkbox at the top right.
      </span>
    </v-snackbar>
  </v-container>
</template>

<script>
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import { mapActions, mapState, mapGetters } from 'vuex';
import { actions, state, getters } from '@/store/modules/cohortManager/types';
import {
  getCollectionDescription,
  getLongScaleNameDefault,
} from '@/utils/helpers';

import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import ManageCohortsTable from '@/components/CohortManager/ManageCohortsTable.vue';
import AnalyticsTable from '@/components/CohortManager/AnalyticsTable.vue';
import AnalyticsPopup from '@/components/CohortManager/AnalyticsPopup.vue';
import InputVariables from '@/components/CohortManager/InputVariables.vue';
import OutputVariables from '@/components/CohortManager/OutputVariables.vue';

export default {
  name: 'CohortManager',
  components: {
    AnalysisTracker,
    InputVariables,
    OutputVariables,
    ManageCohortsTable,
    AnalyticsTable,
    AnalyticsPopup,
    Splitpanes,
    Pane,
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
      substep: '2.1',
      inExpanded: true,
      outExpanded: false,
      inHighlighted: true,
      outHighlighted: false,
      getCollectionDescription: getCollectionDescription,
      analyticsPopupName: 'Tertiles',
      analyticsPopupCohortPrefix: '',
      analyticsPopupCohorts: [],
      analyticsPopupSelectRangeFn: x => x,
      helpModeCheckbox: false,
      helpModeNotify: false,
    };
  },
  computed: {
    ...mapGetters('cohortManager', {
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      cohort: state.COHORT,
      cohorts: state.COHORTS,
      inputVariables: state.INPUT_VARIABLES,
      outputVariables: state.OUTPUT_VARIABLES,
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      helpMode: state.HELP_MODE,
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
      // sort most recent first
      // using id because resolution of date_generated isn't sufficiently high res
      var scc = [...cch].sort((x, y) => y['id'] - x['id']);
      return scc;
    },
    allPanelsClass() {
      var cl = 'ma-0 pa-0 pt-2';
      if (this.helpMode && this.substep == '2.4') {
        cl = cl + ' help_mode';
      }
      return cl;
    },
    inputVarsClass() {
      var cl = 'ma-0 pt-0';
      if (this.helpMode && (this.substep == '2.1' || this.substep == '2.3')) {
        cl = cl + ' help_mode';
      }
      return cl;
    },
    outputVarsClass() {
      var cl = 'ma-0 pt-0 mr-1';
      if (this.helpMode && this.substep == '2.2') {
        cl = cl + ' help_mode';
      }
      return cl;
    },
    inputVarsStyle() {
      if (this.helpMode && this.substep != '2.2') {
        return 'z-index: 100;';
      }
      return 'z-index: auto';
    },
    manageCohortsStyle() {
      // always show Manage Cohorts in Help Mode:
      if (this.helpMode) {
        return 'z-index: 100;';
      }
      return 'z-index: auto';
    },
    outputVarsStyle() {
      if (this.helpMode && (this.substep == '2.2' || this.substep == '2.4')) {
        return 'z-index: 100;';
      }
      return 'z-index: auto';
    },
    analyticsTableStyle() {
      if (this.helpMode && this.substep == '2.4') {
        return 'z-index: 100;';
      }
      return 'z-index: auto';
    },
  },
  watch: {
    substep() {
      if (this.substep === '2.1') {
        //        this.inExpanded = true;
        //        this.outExpanded = false;
        this.inHighlighted = true;
        this.outHighlighted = false;
      } else if (this.substep === '2.2') {
        //        this.inExpanded = false;
        //        this.outExpanded = true;
        this.inHighlighted = false;
        this.outHighlighted = true;
      } else if (this.substep === '2.3') {
        //        this.inExpanded = true;
        //        this.outExpanded = true;
        this.inHighlighted = true;
        this.outHighlighted = false;
      } else if (this.substep === '2.4') {
        this.inHighlighted = false;
        this.outHighlighted = false;
      }
    },
    inputVariables(iv) {
      this.updateSubstep();
    },
    outputVariables(ov) {
      this.updateSubstep();
    },
    filteredData(fd) {
      this.updateSubstep();
    },
    unfilteredData(ufd) {
      this.updateSubstep();
    },
    helpModeCheckbox(helpOn) {
      if (helpOn != this.helpMode) this.setHelpMode(helpOn);
    },
    helpMode(helpOn) {
      this.helpModeNotify = helpOn;
    },
  },
  async created() {
    this.resetAllStoreData();
    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    await this.fetchCohorts();
    this.newCohort();
    var datasets = this.collection.studies.map(d => d.study);
    var useLongScaleNames = getLongScaleNameDefault(datasets);
    this.setUseLongScaleNames(useLongScaleNames);
    this.isLoading = false;
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchCohorts: actions.FETCH_COHORTS,
      fetchData: actions.FETCH_DATA,
      resetAllStoreData: actions.RESET_ALL_STORE_DATA,
      setCohort: actions.SET_COHORT,
      setCohortNoReset: actions.SET_COHORT_NO_RESET,
      setUseLongScaleNames: actions.SET_USE_LONG_SCALE_NAMES,
      setHelpMode: actions.SET_HELP_MODE,
    }),
    updateSubstep() {
      var n_iv = this.inputVariables.length;
      var n_ov = this.outputVariables.length;
      var has_filters = this.filteredData.length < this.unfilteredData.length;
      var new_ss = this.substep;

      if (n_iv > 0 && n_ov > 0 && has_filters) {
        new_ss = '2.4';
      } else if (n_iv > 0 && n_ov > 0) {
        new_ss = '2.3';
      } else if (n_iv > 0) {
        new_ss = '2.2';
      } else {
        new_ss = '2.1';
      }
      if (new_ss != this.substep) this.substep = new_ss;
    },
    userSelectedVariables() {
      this.setCohortNoReset({ id: -1 });
    },
    userChangedVariable() {
      this.setCohortNoReset({ id: -1 });
    },
    cohortSaved(success) {
      console.log('CohortManager: cohortSaved success=' + success);
      if (this.helpMode) this.createNew(success);
    },
    // create entirely new cohort resetting everything
    createNew(success) {
      // return to "choose predictor variables" step
      this.setNewCohort({ id: null });
      this.substep = '2.1';
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
      this.substep = '2.3';
    },
    cohortSelected(newCohort) {
      if (newCohort == this.cohort) {
        return;
      }
      this.setNewCohort(newCohort);
      if (
        newCohort.label !== 'New Cohort' &&
        newCohort.label !== 'Choose Cohort'
      ) {
        this.substep = '2.3';
      } else {
        this.substep = '2.1';
      }
    },
    newCohort() {
      this.setNewCohort({ id: -1, label: 'New Cohort' });
    },
    cohortDeleted() {
      this.substep = '2.1';
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
    async comparePredefinedRanges(ranges) {
      this.analyticsPopupCohorts = ranges.cohorts;
      this.analyticsPopupName = ranges.name;
      this.analyticsPopupCohortPrefix = ranges.dimension_name + ' - ';
      this.analyticsPopupSelectRangeFn = ranges.select_fn;
      this.$refs.apop.show(true);
    },
    async savePredefinedRanges(ranges) {
      this.analyticsPopupCohorts = ranges.cohorts;
      this.analyticsPopupName = ranges.name;
      this.analyticsPopupCohortPrefix = ranges.dimension_name + ' - ';
      this.analyticsPopupSelectRangeFn = ranges.select_fn;
      this.$refs.apop.saveCohorts(
        ranges.cohorts,
        this.analyticsPopupCohortPrefix
      );
    },
  },
};
</script>

<style scoped>
/* Help mode */
.help_mode {
  border: 7px solid #fceb3b !important;
}
</style>
