<template>
  <v-container v-if="isLoading" fluid fill-width class="ma-0 pa-2">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0"> <loading-spinner /> </v-col>
    </v-row>
  </v-container>

  <v-container
    v-else
    fluid
    fill-width
    class="ma-0 pa-0"
    center="start"
    justify="start"
  >
    <v-row class="pa-0 ma-0">
      <v-col cols="12" class="pa-0 ma-0">
        <v-container
          fluid
          fill-width
          class="ma-0 pa-2"
          center="start"
          justify="start"
        >
          <v-app-bar
            app
            :class="useAutomatedAnalysisMode ? 'purple' : 'primary'"
          >
            <v-icon color="white" x-large>analytics</v-icon>
            <v-toolbar-title class="white--text pl-3"
              >Data Analytics
              <div class="subheading">
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

            <v-chip
              v-if="useAutomatedAnalysisMode"
              color="white"
              text-color="purple"
              class="mr-1"
              :disabled="!useAutomatedAnalysisMode"
              >Auto Mode ON</v-chip
            >
          </v-app-bar>

          <analysis-tracker
            step="3"
            :substep="substep"
            :collection-id="collectionId"
          ></analysis-tracker>

          <v-container fluid fill-width class="ma-0 pa-0 pt-1">
            <v-row class="ma-0 pa-0 pt-2">
              <v-col cols="12" class="ma-0 pa-0">
                <v-sheet color="white" height="100%" class="rounded-lg shadow">
                  <v-container fluid fill-width class="ma-0 pa-0">
                    <v-row class="ma-0 pa-0">
                      <v-col cols="12" class="ma-0 pa-0">
                        <cohort-table
                          ref="cohortTable"
                          title="ANALYZE COHORTS"
                          :cohorts="selectedCohorts"
                          :select-cohorts="visibleCohorts"
                          :disable-pagination="false"
                          show-select
                          show-colors
                          report-max-selected-overlap
                          checkbox-tooltip="Check to include this cohort in the next analysis."
                          @selectedCohorts="updateVisibleCohorts"
                        />
                      </v-col>
                    </v-row>

                    <v-row class="ma-0 pa-0">
                      <v-col cols="12" class="ma-0 pa-0">
                        <v-container v-if="collection.is_longitudinal" fluid>
                          <span
                            class="primary--text subtitle-1 font-weight-bold mb-1"
                            >Analysis Measure:</span
                          ><v-radio-group
                            v-model="selectedComparisonMeasure"
                            hide-details
                            row
                            dense
                            class="ma-0 pa-0"
                          >
                            <v-radio
                              v-for="m in comparisonMeasures"
                              :key="m.value"
                              :label="m.label"
                              :value="m"
                            ></v-radio>
                          </v-radio-group>
                        </v-container>

                        <v-btn
                          class="primary text--white ma-0 px-2 py-0 mx-3 mb-2"
                          :disabled="!twoOrMoreCohortsSelected"
                          @click="analyzeCohortList(visibleCohorts)"
                          ><v-icon large class="pr-2" color="white"
                            >analytics</v-icon
                          >
                          Analyze
                          {{
                            twoOrMoreCohortsSelected
                              ? visibleCohorts.length
                              : ''
                          }}
                          Selected Cohorts</v-btn
                        >
                      </v-col>
                    </v-row>
                  </v-container>
                </v-sheet>
              </v-col>
            </v-row>

            <v-row class="ma-0 pa-0 pt-2" min-height="400px">
              <v-col cols="12" class="ma-0 pa-0">
                <analysis-list
                  :analyses="analyses"
                  @deleteAnalysis="deleteAnalysis"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-container>
      </v-col>
    </v-row>

    <v-dialog v-model="aaDialog" persistent scrollable max-width="40%">
      <v-card class="rounded-lg" style="border: 3px solid #3f51b5;">
        <v-card-title color="white" class="ma-0 pa-2" primary-title>
          <span class="primary--text text--darken-3 title"
            >Automated Analysis Mode: Run Analyses</span
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
		<v-list v-if="s.title == 'Running analyses' && aaAnalyses.length > 0">
		  <v-list-item v-for="(c, i) in aaAnalyses">
		    <v-list-item-content>
		      {{ c }}
		      </v-list-item-content>
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
            :disabled="aaProgress < 3"
            class="primary white--text ma-0 px-2 mx-2"
            @click="aaDialog = false"
          >
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import CohortTable from '@/components/common/CohortTable.vue';
import AnalysisList from '@/components/DataExplorer/AnalysisList.vue';
import { getCollectionDescription } from '@/utils/helpers';
import { colors } from '@/utils/colors';
import logEvent from '@/utils/logging';

const COMPARISON_MEASURES = [
  {
    label: 'Change',
    value: 'change',
    descr: 'First visit - Last visit change',
  },
  {
    label: 'First Visit',
    value: 'firstVisit',
    descr: 'First visit measurements',
  },
  { label: 'Last Visit', value: 'lastVisit', descr: 'Last visit measurements' },
];

var aaSteps = [
  { title: 'Loading cohorts' },
  { title: 'Running analyses' },
  { title: 'Done' },
];

export default {
  components: {
    AnalysisTracker,
    AnalysisList,
    CohortTable,
  },
  props: {
    collectionId: {
      type: Number,
      required: true,
    },
    variableId: {
      type: Number,
      required: false,
      default: undefined,
    },
    // comma-delimited list of cohort ids to display
    cohortIds: {
      type: String,
      required: false,
      default: undefined,
    },
    // comma-delimited list of cohort ids to select
    visibleCohortIds: {
      type: String,
      required: false,
      default: undefined,
    },
    aaPredictors: {
      type: Array,
      default: () => [],
    },
    aaOutputs: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      isLoading: false,
      selectedCohorts: [],
      expandAnalytics: true,
      // TODO - assign stable color to each newly-created cohort (in CohortManager?)
      colors: colors,
      getCollectionDescription: getCollectionDescription,
      analyses: [],
      analysisNum: 0,
      comparisonMeasures: COMPARISON_MEASURES,
      selectedComparisonMeasure: COMPARISON_MEASURES[2],
      aaDialog: false,
      aaProgress: 0,
      aaLastUpdate: null,
      aaMinStepTime: 1,
      aaSteps: aaSteps,
      aaAnalyses: [],
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      cohorts: state.COHORTS,
      data: state.DATA,
      detailedView: state.DETAILED_VIEW,
      visibleCohorts: state.VISIBLE_COHORTS,
      collection: state.COLLECTION,
      outcomeVariables: state.OUTCOME_VARIABLES,
    }),
    collectionCohorts() {
      var cc = [];
      var collectionId = this.collection.id;
      this.cohorts.forEach(c => {
        if (c.collection_id == collectionId) {
          cc.unshift(c);
        }
      });
      return cc;
    },
    twoOrMoreCohortsSelected() {
      return this.visibleCohorts.length >= 2;
    },
    substep() {
      var ss = this.visibleCohorts.length > 1 ? '3.2' : '3.1';
      return ss;
    },
    useAutomatedAnalysisMode() {
      return this.aaPredictors.length + this.aaOutputs.length > 0;
    },
  },
  watch: {
    // workaround to force DetailedViewChart resize when expandAnalytics toggled
    expandAnalytics() {
      this.$refs.dview.onResize();
    },
  },
  async created() {
    this.isLoading = true;
    if (this.useAutomatedAnalysisMode) {
      this.aaDialog = true;
      this.aaProgress = 0;
    }
    await this.clearData();
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    await this.fetchCohorts();

    // set outcome variables to union of cohort output variables
    const varsAdded = {};
    const outcomeVars = [];

    // determine selected cohorts and assign colors
    var selectedCohorts = this.getCohortsFromIdList(this.cohortIds);
    // if nothing selected then include all cohorts
    if (!selectedCohorts || selectedCohorts.length === 0) {
      selectedCohorts = this.collectionCohorts;
    }
    var scc = [...selectedCohorts].sort((x, y) => y['id'] - x['id']);
    this.selectedCohorts = scc;

    let ind = 0;
    let n_colors = this.colors['cohorts'].length;

    // additional color palettes for male/female cohorts - these will be checked in order
    var palettes = [
      {
        regex: new RegExp('female', 'i'),
        colors: ['#f781bf', '#fddaec', '#fb9a99', '#fccde5'],
        ind: 0,
      },
      {
        regex: new RegExp('male', 'i'),
        colors: ['#1f78b4', '#80b1d3', '#b3cde3', '#a6cee3'],
        ind: 0,
      },
    ];

    this.selectedCohorts
      .filter(v => v.collection_id === this.collectionId)
      .forEach(c => {
        var matched = false;
        palettes.forEach(p => {
          if (!matched && c.label.match(p['regex'])) {
            var nc = p['colors'].length;
            c.color = p['colors'][p['ind'] % nc];
            p['ind'] += 1;
            matched = true;
          }
        });
        if (!matched) {
          c.color = this.colors['cohorts'][ind % n_colors];
          ind += 1;
        }

        const outputVars = c.output_variables;
        outputVars.forEach(ov => {
          const { id } = ov.observation_ontology;
          if (!(id in varsAdded)) {
            varsAdded[id] = 1;
            outcomeVars.push(ov.observation_ontology);
          }
        });
      });

    await this.setOutcomeVariables(outcomeVars);
    //    await this.analyzeCohorts(this.selectedCohorts);

    // initialize page with preselected variable in the highlight view
    if (
      typeof this.variableId !== 'undefined' &&
      !Number.isNaN(this.variableId)
    ) {
      let outVar = null;
      outcomeVars.forEach(ov => {
        if (ov.id === this.variableId) {
          outVar = ov;
        }
      });
      this.setDetailedView(outVar);
    } else {
      this.setDetailedView(null);
    }

    // preselect cohorts in visibleCohortIds
    var vc = this.getCohortsFromIdList(this.visibleCohortIds);
    this.setVisibleCohorts(vc);
    this.isLoading = false;

    if (this.useAutomatedAnalysisMode) {
      this.doAutomatedAnalysis();
    }
  },
  methods: {
    ...mapActions('dataExplorer', {
      analyzeCohorts: actions.ANALYZE_COHORTS,
      fetchCohorts: actions.FETCH_COHORTS,
      fetchCollection: actions.FETCH_COLLECTION,
      clearData: actions.CLEAR_DATA,
      fetchData: actions.FETCH_DATA,
      setOutcomeVariables: actions.SET_OUTCOME_VARIABLES,
      setDetailedView: actions.SET_DETAILED_VIEW,
      setVisibleCohorts: actions.SET_VISIBLE_COHORTS,
    }),
    variableSelected(nv) {
      this.setDetailedView(nv);
    },
    analyticsExpandClicked(nv) {
      this.expandAnalytics = nv;
    },
    updateVisibleCohorts(vc) {
      this.setVisibleCohorts(vc);
    },
    getCohortsFromIdList(idList) {
      var sc = [];
      if (typeof idList !== 'undefined' && idList !== '') {
        const cids = {};
        var collectionId = this.collection.id;
        idList.split(',').forEach(c => {
          cids[c] = 1;
        });
        this.cohorts.forEach(c => {
          if (c.collection_id === collectionId && c.id in cids) {
            sc.push(c);
          }
        });
      }
      return sc;
    },
    logAnalysisStatusChange(analysis) {
      logEvent(
        this.$gtag,
        null,
        null,
        'analysis_status_change',
        'analysis',
        'analysis #' + analysis.index + ' ' + analysis.status
      );
    },
    analyzeCohortList(cohorts) {
      var sortedCohorts = [...cohorts].sort((x, y) => y['id'] - x['id']);

      // union cohort outcome variables
      const varsAdded = {};
      const inputVariables = [];
      const outputVariables = [];

      sortedCohorts.forEach(c => {
        const inputVars = c.input_variables;
        inputVars.forEach(iv => {
          if (iv.subject_ontology != null) {
            const { id } = iv.subject_ontology;
            if (!(id in varsAdded)) {
              varsAdded[id] = 1;
              inputVariables.push(iv.subject_ontology);
            }
          } else {
            const { id } = iv.observation_ontology;
            var key = id + ':' + iv.dimension_label;
            if (!(key in varsAdded)) {
              varsAdded[key] = 1;
              inputVariables.push(iv);
            }
          }
        });
        const outputVars = c.output_variables;
        outputVars.forEach(ov => {
          if (ov.observation_ontology != null) {
            const { id } = ov.observation_ontology;
            if (!(id in varsAdded)) {
              varsAdded[id] = 1;
              ov.observation_ontology.is_longitudinal = this.collection.is_longitudinal;
              outputVariables.push(ov.observation_ontology);
            }
          }
        });
      });

      // run analysis
      var analysis = {
        index: ++this.analysisNum,
        cohorts: sortedCohorts,
        predictorVariables: inputVariables,
        outcomeVariables: outputVariables,
        pvals: null,
        collection: this.collection,
      };

      // create group of samples for each cohort:
      const groups = [];
      sortedCohorts.forEach(c => {
        if (c.collection_id === this.collection.id) {
          const subjids = [];
          c.subject_ids.forEach(sid => {
            subjids[sid] = 1;
          });
          const cohortData = this.data.filter(d => d.subject_id in subjids);
          groups.push(cohortData);
        }
      });
      const numGroups = groups.length;
      const comparisonField = this.selectedComparisonMeasure.value;
      const comparisonFieldDescr = this.selectedComparisonMeasure.label;
      const comparisonFieldLongDescr = this.selectedComparisonMeasure.descr;

      analysis.input = {
        numGroups,
        groups,
        outputVariables,
        comparisonField,
        comparisonFieldDescr,
        comparisonFieldLongDescr,
      };

      logEvent(
        this.$gtag,
        null,
        null,
        'new_analysis',
        'analysis',
        'analysis #' +
          analysis.index +
          ' measure=' +
          analysis.input.comparisonFieldDescr +
          ' cohorts=' +
          analysis.cohorts.map(c => c.label).join(',')
      );

      analysis.status = 'Running';
      analysis.statusTime = new Date().getTime();
      this.logAnalysisStatusChange(analysis);
      var vm = this;

      axios
        .post(`/api/compute-anova`, analysis.input)
        .then(function(response) {
          const { data } = response;
          analysis.pvals = data.pvals;
          analysis.statusTime = new Date().getTime();
          analysis.status = 'Completed';
          vm.logAnalysisStatusChange(analysis);
        })
        .catch(function(err) {
          analysis.statusTime = new Date().getTime();
          analysis.error = err;
          analysis.status = 'Failed';
          vm.logAnalysisStatusChange(analysis);
        });

      this.analyses.unshift(analysis);
      // clear cohort selection
      this.$refs.cohortTable.deselectAll();
    },
    deleteAnalysis(anum) {
      logEvent(
        this.$gtag,
        null,
        null,
        'analysis_deleted',
        'analysis',
        'analysis #' + this.analyses[anum].index
      );
      var new_analyses = [...this.analyses];
      new_analyses.splice(anum, 1);
      this.analyses = new_analyses;
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
      await this.updateAutomatedAnalysisProgress(1);

      // group cohorts by input var
      var ivc = {};
      var ct = this.$refs.cohortTable;
      ct.cohorts.forEach(c => {
        var ivs = c.input_variables.filter(v =>
          c.label.startsWith(v.subject_ontology.abbreviation + ' - ')
        );
        if (ivs.length == 1) {
          var key = ivs[0].subject_ontology.abbreviation;
          if (!(key in ivc)) {
            ivc[key] = [];
          }
          ivc[key].push(c);
        }
      });

      var keys = Object.keys(ivc);
      for (var i = 0; i < keys.length; ++i) {
        var cohorts = ivc[keys[i]];
	this.aaAnalyses.push(keys[i] + " - " + cohorts.length + " cohorts");
	this.analyzeCohortList(cohorts);
        await this.sleep(this.aaMinStepTime * 1000);
      }

      await this.updateAutomatedAnalysisProgress(2);
      await this.updateAutomatedAnalysisProgress(3);
    },
  },
};
</script>

<style scoped></style>
