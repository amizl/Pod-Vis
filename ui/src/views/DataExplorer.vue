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
          <v-app-bar app class="primary">
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
                        <v-container fluid>
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
  },
  watch: {
    // workaround to force DetailedViewChart resize when expandAnalytics toggled
    expandAnalytics() {
      this.$refs.dview.onResize();
    },
  },
  async created() {
    this.isLoading = true;
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
    this.selectedCohorts
      .filter(v => v.collection_id === this.collectionId)
      .forEach(c => {
        c.color = this.colors['cohorts'][ind % n_colors];
        ind += 1;
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
    analyzeCohortList(cohorts) {
      var sortedCohorts = [...cohorts].sort((x, y) => y['id'] - x['id']);

      // union cohort outcome variables
      const varsAdded = {};
      const inputVariables = [];
      const outputVariables = [];

      sortedCohorts.forEach(c => {
        const inputVars = c.input_variables;
        inputVars.forEach(iv => {
          const { id } = iv.subject_ontology;
          if (!(id in varsAdded)) {
            varsAdded[id] = 1;
            inputVariables.push(iv.subject_ontology);
          }
        });
        const outputVars = c.output_variables;
        outputVars.forEach(ov => {
          const { id } = ov.observation_ontology;
          if (!(id in varsAdded)) {
            varsAdded[id] = 1;
            ov.observation_ontology.is_longitudinal = this.collection.is_longitudinal;
            outputVariables.push(ov.observation_ontology);
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
      analysis.status = 'Running';
      analysis.statusTime = new Date().getTime();

      axios
        .post(`/api/compute-anova`, analysis.input)
        .then(function(response) {
          const { data } = response;
          analysis.pvals = data.pvals;
          analysis.status = 'Completed';
          analysis.statusTime = new Date().getTime();
        })
        .catch(function(err) {
          analysis.status = 'Failed';
          analysis.statusTime = new Date().getTime();
          analysis.error = err;
        });

      this.analyses.unshift(analysis);
      // clear cohort selection
      this.$refs.cohortTable.deselectAll();
    },
    deleteAnalysis(anum) {
      var new_analyses = [...this.analyses];
      new_analyses.splice(anum, 1);
      this.analyses = new_analyses;
    },
  },
};
</script>

<style scoped></style>
