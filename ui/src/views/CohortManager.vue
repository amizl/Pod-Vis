<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0"> <loading-spinner /> </v-col>
    </v-row>
  </v-container>

  <v-container v-else fluid fill-width class="ma-0 pa-2">
    <v-app-bar app :class="useAutomatedAnalysisMode ? 'purple' : 'primary'">
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

      <v-chip
        v-if="useAutomatedAnalysisMode"
        color="white"
        text-color="purple"
        class="mr-1"
        :disabled="!useAutomatedAnalysisMode"
        >Auto Mode ON</v-chip
      >

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

      <v-chip
        v-if="showNextHelpChip"
        label
        close
        color="#4caf50"
        class="font-weight-bold white--text pa-2 my-1 mr-2 ml-4"
        @click:close="showNextHelpChip = false"
        >Click DATA ANALYTICS to proceed to the analysis step.</v-chip
      >

      <analysis-summary-btn-dialog
        ref="asum_btn"
        :collection-id="collectionId"
        class="ml-3"
      ></analysis-summary-btn-dialog>
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
        class="pb-2"
        :substep.sync="substep"
        :collection-id="collectionId"
        @createSimilar="createSimilar"
        @createNew="createNew"
        @nextStep="nextStep"
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
                      ref="input_vars"
                      :expanded.sync="inExpanded"
                      :highlighted="inHighlighted"
                      :class="inputVarsClass"
                      :show-add-help="helpMode && substep == '2.1'"
                      :show-filter-help="
                        helpMode && substep == '2.3' && !hasFilters
                      "
                      :show-analytics-help="
                        helpMode && substep == '2.3' && hasFilters
                      "
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
                    :show-save-help="helpMode && substep == '2.3' && hasFilters"
                    @selectedCohort="cohortSelected"
                    @savedCohort="cohortSaved"
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
                    ref="output_vars"
                    :expanded.sync="outExpanded"
                    :highlighted="outHighlighted"
                    :disabled="true"
                    :class="outputVarsClass"
                    :show-add-help="helpMode && substep == 2.2"
                    :show-review-help="helpMode && substep == 2.3 && hasFilters"
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
                  <analytics-table
                    class="ml-1"
                    color-scheme="brewer5"
                    :show-review-help="helpMode && substep == 2.3 && hasFilters"
                  />
                </pane>
              </splitpanes>
            </v-col>
          </v-row>

          <v-overlay
            absolute
            :value="helpMode && (substep != 2.3 || !hasFilters)"
          >
          </v-overlay>
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
    <v-dialog v-model="aaDialog" persistent scrollable max-width="40%">
      <v-card class="rounded-lg" style="border: 3px solid #3f51b5;">
        <v-card-title color="white" class="ma-0 pa-2" primary-title>
          <span class="primary--text text--darken-3 title"
            >Automated Analysis Mode: Create Cohorts</span
          >
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="py-4">
          <v-list>
            <v-list-item
              v-for="(s, i) in aaSteps"
              :key="`prog-${i}`"
              :disabled="i > aaProgress"
            >
              <v-list-item-content>
                {{ s.title }}
                <v-list
                  v-if="s.title == 'Creating cohorts' && aaCohorts.length > 0"
                >
                  <v-list-item v-for="(c, ci) in aaCohorts" :key="`aac-${ci}`">
                    <v-list-item-content> {{ c }} </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-list-item-content>
              <v-list-item-avatar>
                <v-icon v-if="i < aaProgress">done</v-icon>
              </v-list-item-avatar>
            </v-list-item>
          </v-list>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            :disabled="aaProgress < 4"
            class="primary white--text ma-0 px-2 mx-2"
            @click="aaToDataAnalytics()"
          >
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
import logEvent from '@/utils/logging';

import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import ManageCohortsTable from '@/components/CohortManager/ManageCohortsTable.vue';
import AnalyticsTable from '@/components/CohortManager/AnalyticsTable.vue';
import AnalyticsPopup from '@/components/CohortManager/AnalyticsPopup.vue';
import InputVariables from '@/components/CohortManager/InputVariables.vue';
import OutputVariables from '@/components/CohortManager/OutputVariables.vue';
import AnalysisSummaryBtnDialog from '@/components/DataExplorer/AnalysisSummaryBtnDialog.vue';

var aaSteps = [
  { title: 'Loading data' },
  { title: 'Adding predictor variables' },
  { title: 'Adding outcome variables' },
  { title: 'Creating cohorts' },
  { title: 'Done' },
];

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
    AnalysisSummaryBtnDialog,
  },
  props: {
    collectionId: {
      type: Number,
      required: true,
    },
    aaPredictors: {
      type: Array,
      default: () => [],
    },
    aaOutputs: {
      type: Array,
      default: () => [],
    },
    aaRanges: {
      type: String,
      default: '',
    },
    aaMCS: {
      type: String,
      default: '',
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
      showNextHelpChip: false,
      aaDialog: false,
      aaProgress: 0,
      aaLastUpdate: null,
      aaMinStepTime: 1,
      aaSteps: aaSteps,
      aaCohorts: [],
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
      var cl = 'ma-0 pa-0';
      if (this.helpMode && this.substep == '2.3' && this.hasFilters) {
        cl = cl + ' help_mode';
      }
      return cl;
    },
    inputVarsClass() {
      var cl = 'ma-0 pt-0';
      if (
        this.helpMode &&
        (this.substep == '2.1' || (this.substep == '2.3' && !this.hasFilters))
      ) {
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
      if (
        this.helpMode &&
        (this.substep == '2.2' || (this.substep == '2.3' && this.hasFilters))
      ) {
        return 'z-index: 100;';
      }
      return 'z-index: auto';
    },
    analyticsTableStyle() {
      if (this.helpMode && this.substep == '2.3' && this.hasFilters) {
        return 'z-index: 100;';
      }
      return 'z-index: auto';
    },
    showNextHelp() {
      return this.helpMode && this.collection_cohorts.length >= 2;
    },
    hasFilters() {
      return this.filteredData.length < this.unfilteredData.length;
    },
    useAutomatedAnalysisMode() {
      return this.aaPredictors.length + this.aaOutputs.length > 0;
    },
  },
  watch: {
    substep() {
      if (this.substep === '2.1') {
        this.inHighlighted = true;
        this.outHighlighted = false;
      } else if (this.substep === '2.2') {
        this.inHighlighted = false;
        this.outHighlighted = true;
      } else if (this.substep === '2.3') {
        if (this.hasFilters) {
          this.inHighlighted = false;
          this.outHighlighted = false;
        } else {
          this.inHighlighted = true;
          this.outHighlighted = false;
        }
      }
    },
    inputVariables() {
      this.updateSubstep();
    },
    outputVariables() {
      this.updateSubstep();
    },
    filteredData() {
      this.updateSubstep();
    },
    unfilteredData() {
      this.updateSubstep();
    },
    helpModeCheckbox(helpOn) {
      if (helpOn != this.helpMode) this.setHelpMode(helpOn);
    },
    helpMode(helpOn) {
      this.helpModeNotify = helpOn;
      logEvent(
        this.$gtag,
        null,
        null,
        'helpmode_' + (helpOn ? 'on' : 'off'),
        'help',
        this.substep
      );
    },
    showNextHelp(show) {
      this.showNextHelpChip = show;
    },
  },
  async mounted() {
    // reset help mode to false
    this.setHelpMode(false);
  },
  async created() {
    if (this.useAutomatedAnalysisMode) {
      this.aaDialog = true;
      this.aaProgress = 0;
    }
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
    if (this.useAutomatedAnalysisMode) {
      this.doAutomatedAnalysis();
    }
  },
  methods: {
    ...mapActions('cohortManager', {
      clearAllFilters: actions.CLEAR_ALL_FILTERS,
      fetchCollection: actions.FETCH_COLLECTION,
      fetchCohorts: actions.FETCH_COHORTS,
      fetchData: actions.FETCH_DATA,
      resetAllStoreData: actions.RESET_ALL_STORE_DATA,
      setCohort: actions.SET_COHORT,
      setCohortNoReset: actions.SET_COHORT_NO_RESET,
      setUseLongScaleNames: actions.SET_USE_LONG_SCALE_NAMES,
      setHelpMode: actions.SET_HELP_MODE,
      setInputVariables: actions.SET_INPUT_VARIABLES,
      setOutputVariables: actions.SET_OUTPUT_VARIABLES,
      saveCohort: actions.SAVE_COHORT,
    }),
    updateSubstep() {
      var n_iv = this.inputVariables.length;
      var n_ov = this.outputVariables.length;
      var new_ss = this.substep;

      if (n_iv > 0 && n_ov > 0) {
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
      if (success) {
        // reset all filters
        this.clearAllFilters();
        // return to "add filters" step
        this.substep = '2.3';
      }
    },
    // create entirely new cohort resetting everything
    createNew(success) {
      if (success) {
        // return to "choose predictor variables" step
        this.setNewCohort({ id: null });
        this.substep = '2.1';
      }
    },
    // create new cohort similar to the most-recently-created one
    createSimilar(success) {
      if (success) {
        var ncc = this.collection_cohorts.length;
        // load last cohort in the list
        if (ncc > 0) {
          var last_cohort = this.collection_cohorts[ncc - 1];
          this.setNewCohort(last_cohort);
        }
        // return to "add filters" step
        this.substep = '2.3';
      }
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
    nextStep() {
      this.$refs.asum_btn.dialog = true;
    },
    // TODO - copied from DataSummary
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    async updateAutomatedAnalysisProgress(progress) {
      var ts = Date.now();
      if (this.aaLastUpdate == null) {
        this.aaProgress = progress;
      } else {
        var diff = (ts - this.aaLastUpdate) / 1000.0;
        if (diff < this.aaMinStepTime) {
          var remaining = this.aaMinStepTime - diff;
          await this.sleep(remaining * 1000);
        }
        this.aaProgress = progress;
      }
      this.aaLastUpdate = Date.now();
    },
    async doAutomatedAnalysis() {
      await this.updateAutomatedAnalysisProgress(0);

      var aa_ph = {};
      this.aaPredictors.map(vid => {
        aa_ph[vid] = true;
      });
      var aa_oh = {};
      this.aaOutputs.map(vid => {
        aa_oh[vid] = true;
      });

      // ** add predictor variables
      await this.updateAutomatedAnalysisProgress(1);
      var ivd = this.$refs.input_vars.$refs.input_toolbar.$refs.input_dialog;
      // open input vars dialog
      ivd.openInputVariableDialog = true;
      await this.sleep(this.aaMinStepTime * 1000);

      // select input vars
      ivd.inputVariables.forEach(v => {
        if (v.id in aa_ph) {
          v.inmSelected = true;
          ivd.masterCbChange(v);
        }
      });
      await this.sleep(this.aaMinStepTime * 2000);

      // close input vars dialog
      ivd.openInputVariableDialog = false;

      await this.updateAutomatedAnalysisProgress(2);
      await this.sleep(this.aaMinStepTime * 1000);

      // ** add outcome variables
      var ovd = this.$refs.output_vars.$refs.output_toolbar.$refs.output_dialog;

      // open output vars dialog
      ovd.openOutputVariableDialog = true;
      await this.sleep(this.aaMinStepTime * 1000);

      // select output vars
      ovd.outputVariables.forEach(v => {
        if (v.id in aa_oh) {
          v.outmSelected = true;
          ovd.masterCbChange(v);
        }
      });
      await this.sleep(this.aaMinStepTime * 2000);

      // close output vars dialog
      ovd.openOutputVariableDialog = false;

      await this.updateAutomatedAnalysisProgress(3);
      await this.sleep(this.aaMinStepTime * 1000);

      // unpack aaRanges, aaMCS
      // TODO - copied from SaveCollectionBtnDialog
      const d1 = '|';
      const d2 = '||';
      const vranges = {};
      this.aaRanges.split(d2).map(r => {
        var [k, v] = r.split(d1);
        v.split(',').map(vid => {
          vranges[vid] = k;
        });
      });
      const vmcs = {};
      this.aaMCS.split(d2).map(r => {
        var [k, v] = r.split(d1);
        v.split(',').map(vid => {
          vmcs[vid] = k;
        });
      });

      // create cohorts for each predictor variable
      var ivc = this.$refs.input_vars.$refs.input_charts;
      var hist_charts = [];
      var col_charts = [];

      ivd.inputVariables.forEach(v => {
        if (ivc.$refs['ivc-' + v.id]) {
          if ('hist_chart' in ivc.$refs['ivc-' + v.id][0].$refs) {
            var hc = ivc.$refs['ivc-' + v.id][0].$refs.hist_chart;
            hc.tab = 'predef';
            if (v.id in vranges) {
              hc.predef_radio = vranges[v.id];
            } else {
              hc.predef_radio = 'quartiles';
            }
            hist_charts.push(hc);
          } else if ('col_chart' in ivc.$refs['ivc-' + v.id][0].$refs) {
            var cc = ivc.$refs['ivc-' + v.id][0].$refs.col_chart;
            var cch = { chart: cc, cohorts: [] };
            col_charts.push(cch);

            // minimum category size - all smaller categories will be merged into 'Other'
            var mcs = 1;
            if (v.id in vmcs) {
              mcs = vmcs[v.id];
            }

            // group data by category
            var cat2d = {};
            var cat2c = {};
            this.unfilteredData.map(d => {
              let dv = cc.dimension.accessor(d);
              if (!(dv in cat2d)) {
                cat2d[dv] = [];
                cat2c[dv] = 0;
              }
              cat2d[dv].push(d);
              cat2c[dv] += 1;
            });

            var s_args = {
              collection: this.collection,
              inputVariables: this.inputVariables,
              outputVariables: this.outputVariables,
              minCatSize: mcs,
            };

            // merge smaller categories
            var small_cats = [];
            Object.keys(cat2d).forEach(cat => {
              var ct = cat2c[cat];
              if (ct < mcs) {
                small_cats.push(cat);
              }
              // make single category cohort
              else {
                var queries = {};
                queries[cc.dimensionName] = [{ value: cat }];
                var args = {
                  name: cc.dimensionName + ' - ' + cat,
                  queries: queries,
                  subjectIds: cat2d[cat].map(d => d.subject_id),
                  ...s_args,
                };
                cch['cohorts'].push(args);
              }
            });

            // create multi-category 'Other' category if needed
            if (small_cats.length > 0) {
              var queries = {};
              queries[cc.dimensionName] = small_cats.map(c => {
                return { value: c };
              });
              var subjIds = [];
              small_cats.map(c => {
                cat2d[c].map(d => subjIds.push(d.subject_id));
              });
              var args = {
                name:
                  cc.dimensionName + ' - Other [' + small_cats.join(',') + ']',
                queries: queries,
                subjectIds: subjIds,
                ...s_args,
              };
              cch['cohorts'].push(args);
            }
          }
        }
      });

      // hist_charts
      for (var i = 0; i < hist_charts.length; ++i) {
        this.aaCohorts.push(
          hist_charts[i].dimensionName + ' - ' + hist_charts[i].predef_radio
        );
        await hist_charts[i].savePredefs();
        await this.sleep(this.aaMinStepTime * 1000);
      }

      // col_charts
      for (i = 0; i < col_charts.length; ++i) {
        var cc = col_charts[i];
        var nc = cc['cohorts'].length;
        this.aaCohorts.push(
          cc['chart'].dimensionName + ' - ' + nc + ' cohorts'
        );
        for (var j = 0; j < nc; ++j) {
          await this.saveCohort(cc['cohorts'][j]);
          await this.sleep(this.aaMinStepTime * 1000);
        }
      }

      await this.updateAutomatedAnalysisProgress(4);
      await this.updateAutomatedAnalysisProgress(5);
    },
    // go to data analytics
    aaToDataAnalytics() {
      var query = { collection: this.collection.id };
      if (this.useAutomatedAnalysisMode) {
        query['aa_predictors'] = this.aaPredictors;
        query['aa_outputs'] = this.aaOutputs;
      }

      this.$router.push({ name: 'dataExplorer', query: query });
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
