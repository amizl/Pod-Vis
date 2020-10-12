<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0"> <loading-spinner /> </v-col>
    </v-row>
  </v-container>

  <v-container v-else fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>grid_on</v-icon>
      <v-toolbar-title class="white--text pl-3"
        >Summary Matrix
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

      <v-btn
        v-if="substep === '4.1'"
        color="primary--text"
        :disabled="tableCohortsSelected.length < 2"
        @click="goto4p2()"
      >
        Continue</v-btn
      >
    </v-app-bar>

    <analysis-tracker
      step="4"
      :substep="substep"
      :collection-id="collectionId"
    ></analysis-tracker>

    <!-- Step 4.1 -->
    <v-container
      v-if="substep === '4.1'"
      fluid
      fill-width
      class="ma-0 pa-0 pt-2"
    >
      <v-col cols="12" class="ma-0 pa-0">
        <cohort-table
          title="Choose Cohorts"
          :cohorts="collection_cohorts"
          show-select
          report-max-selected-overlap
          @selectedCohorts="updateSelectedCohorts"
	  disable-pagination
        />
      </v-col>
    </v-container>

    <!-- Step 4.2 -->
    <v-container v-else fluid fill-width class="ma-0 pa-0 pt-2">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <cohort-table
            title="Selected Cohorts"
            :cohorts="selectedCohorts"
            show-colors
            report-max-overlap
          />
        </v-col>
      </v-row>

      <v-row class="ma-0 pa-0 mt-2">
        <v-col :cols="expandAnalytics ? 5 : 3" class="ma-0 pa-0">
          <analytics-panel
            :selected-variable="selectedOutcomeVariable"
            :show-category-icons="true"
            :expanded="expandAnalytics"
            :color-scale-when-minimized="true"
            :color-scheme="colorScheme"
            @variableSelected="variableSelected"
            @expandClicked="analyticsExpandClicked"
          />

          <!-- color scheme chooser -->
          <v-sheet v-if="false" color="white" class="rounded-lg shadow mt-2">
            <v-container fluid fill-width class="ma-0 pa-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <v-sheet color="white" class="rounded-lg shadow">
                    <v-container fluid fill-width class="ma-0 pa-0">
                      <v-row class="ma-0 pa-0">
                        <v-col cols="12" class="ma-0 pa-0">
                          <v-card color="#eeeeee" class="pt-1">
                            <v-card-title class="primary--text pl-3 py-2"
                              >Color Scheme</v-card-title
                            >
                          </v-card>
                        </v-col>
                      </v-row>
                    </v-container>
                  </v-sheet>
                  <div class="pa-2">
                    Select p-Value color scheme:
                    <v-select
                      v-model="colorScheme"
                      dense
                      :items="colorSchemeItems"
                    >
                    </v-select>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
          <!-- end color scheme chooser -->
        </v-col>

        <v-col :cols="expandAnalytics ? 7 : 9" class="ma-0 pa-0 pl-2">
          <tukey-hsd-heatmap :color-scheme="colorScheme" />
        </v-col>
      </v-row>

      <v-row class="ma-0 pa-0 mt-2">
        <v-col cols="12" class="ma-0 pa-0">
	  <box-plots v-if="!selectedOutcomeVariable || (selectedOutcomeVariable.data_category == 'Continuous')" />
	  <div v-else> Categorical var display </div>
	</v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/analysisSummary/types';
import {
  actions as deActions,
  state as deState,
} from '@/store/modules/dataExplorer/types';
import { getCollectionDescription } from '@/utils/helpers';
import { colors } from '@/utils/colors';

import BoxPlots from '@/components/AnalysisSummary/BoxPlots.vue';
import TukeyHsdHeatmap from '@/components/AnalysisSummary/TukeyHSDHeatmap.vue';
import AnalyticsPanel from '@/components/DataExplorer/AnalyticsPanel.vue';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import CohortTable from '@/components/common/CohortTable.vue';

export default {
  name: 'AnalysisSummary',
  components: {
    AnalysisTracker,
    AnalyticsPanel,
    BoxPlots,
    CohortTable,
    TukeyHsdHeatmap,
  },
  props: {
    collectionId: {
      type: Number,
      required: true,
    },
    cohortIds: {
      type: String,
      required: false,
      default: undefined,
    },
  },
  data() {
    return {
      isLoading: false,
      tableCohortsSelected: [],
      expandAnalytics: true,
      getCollectionDescription: getCollectionDescription,
      colors: colors,
      colorScheme: 'brewer5',
      colorSchemeItems: [
        { text: 'Brewer 4 class purples', value: 'brewer4p' },
        { text: 'Brewer 5 class purples', value: 'brewer5p' },
        { text: 'Brewer 6 class reds', value: 'brewer6r' },
        { text: 'Brewer 6 class blues', value: 'brewer6' },
        { text: 'Brewer 5 class blues', value: 'brewer5' },
        { text: 'Brewer 5 class blues B', value: 'brewer5v2' },
        { text: 'Value 80 blues', value: 'val80' },
        { text: 'Value 100 blues', value: 'val100' },
      ],
    };
  },
  computed: {
    ...mapState('analysisSummary', {
      selectedCohorts: state.SELECTED_COHORTS,
      selectedOutcomeVariable: state.SELECTED_OUTCOME_VARIABLE,
    }),
    ...mapState('dataExplorer', {
      cohorts: deState.COHORTS,
      collection: deState.COLLECTION,
      data: deState.DATA,
      outcomeVariables: deState.OUTCOME_VARIABLES,
    }),
    substep() {
      return this.selectedCohorts.length > 0 ? '4.2' : '4.1';
    },
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
    async selectedCohorts(selCohorts) {
      if (selCohorts.length == 0) {
        return;
      }
      await this.analyzeCohortsDE(selCohorts);

      // set outcome variables to union of cohorts' output variables
      const varsAdded = {};
      const outcomeVars = [];
      this.selectedCohorts.forEach(c => {
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
      await this.analyzeCohorts({
        collection: this.collection,
        cohorts: this.selectedCohorts,
        data: this.data,
      });
    },
  },
  async created() {
    this.isLoading = true;
    // reset selected cohorts
    await this.setSelectedOutcomeVariable(null);
    await this.setSelectedCohorts([]);
    await this.clearData();
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    await this.fetchCohorts();
    // set cohorts from cohortIds property, if defined
    var selCohorts = this.getSelectedCohortsFromIdList();
    if (selCohorts.length > 0) {
      this.setCohortColors(selCohorts);
      this.setSelectedCohorts(selCohorts);
    }
    this.isLoading = false;
  },
  methods: {
    ...mapActions('analysisSummary', {
      setSelectedCohorts: actions.SET_SELECTED_COHORTS,
      analyzeCohorts: actions.ANALYZE_COHORTS,
      setSelectedOutcomeVariable: actions.SET_SELECTED_OUTCOME_VARIABLE,
    }),
    ...mapActions('dataExplorer', {
      analyzeCohortsDE: deActions.ANALYZE_COHORTS,
      fetchCohorts: deActions.FETCH_COHORTS,
      fetchCollection: deActions.FETCH_COLLECTION,
      clearData: deActions.CLEAR_DATA,
      fetchData: deActions.FETCH_DATA,
      setOutcomeVariables: deActions.SET_OUTCOME_VARIABLES,
    }),
    variableSelected(v) {
      this.setSelectedOutcomeVariable(v);
    },
    analyticsExpandClicked(nv) {
      this.expandAnalytics = nv;
    },
    // cohorts currently selected in step 4.1
    updateSelectedCohorts(sc) {
      this.tableCohortsSelected = sc;
    },
    // cohorts selected for step 4.2
    getSelectedCohortsFromIdList() {
      var sc = [];
      if (typeof this.cohortIds !== 'undefined' && this.cohortIds !== '') {
        const cids = {};
        var collectionId = this.collection.id;
        this.cohortIds.split(',').forEach(c => {
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
    setCohortColors(cohorts) {
      let ind = 0;
      let view = this;
      let n_colors = this.colors['cohorts'].length;
      cohorts.forEach(c => {
        var nc = view.colors['cohorts'][ind % n_colors];
        c.color = nc;
        ind += 1;
      });
    },
    async updateCohortIds() {
      await this.analyzeCohortsDE(selCohorts);

      // set outcome variables to union of cohorts' output variables
      const varsAdded = {};
      const outcomeVars = [];
      this.selectedCohorts.forEach(c => {
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
      await this.analyzeCohorts({
        collection: this.collection,
        cohorts: this.selectedCohorts,
        data: this.data,
      });
    },
    async goto4p2() {
      var sc = this.tableCohortsSelected;
      this.setCohortColors(sc);
      this.setSelectedCohorts(sc);
    },
  },
};
</script>

<style scoped></style>
