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
        <div class="subheading">Dataset: {{ collection.label }}</div>
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
            report-max-overlap
          />
        </v-col>
      </v-row>

      <v-row class="ma-0 pa-0 mt-2">
        <v-col cols="6" class="ma-0 pa-0">
	  <analytics-panel
	    :show-category-icons="true"
	    />
	</v-col>

        <v-col cols="6" class="ma-0 pa-0 pl-2">
	  <tukey-hsd-grid />
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

import TukeyHsdGrid from '@/components/AnalysisSummary/TukeyHSDGrid.vue';
import AnalyticsPanel from '@/components/DataExplorer/AnalyticsPanel.vue';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import CohortTable from '@/components/common/CohortTable.vue';

export default {
  name: 'AnalysisSummary',
  components: {
    AnalysisTracker,
    AnalyticsPanel,
    TukeyHsdGrid,
    CohortTable,
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
    };
  },
  computed: {
    ...mapState('analysisSummary', {
      selectedCohorts: state.SELECTED_COHORTS,
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
    this.setSelectedCohorts([]);
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    await this.fetchCohorts();
    // set cohorts from cohortIds property, if defined
    var selCohorts = this.getSelectedCohortsFromIdList();
    if (selCohorts.length > 0) {
      this.setSelectedCohorts(selCohorts);
    }
    this.isLoading = false;
  },
  methods: {
    ...mapActions('analysisSummary', {
      setSelectedCohorts: actions.SET_SELECTED_COHORTS,
      analyzeCohorts: actions.ANALYZE_COHORTS,
    }),
    ...mapActions('dataExplorer', {
      analyzeCohortsDE: deActions.ANALYZE_COHORTS,
      fetchCohorts: deActions.FETCH_COHORTS,
      fetchCollection: deActions.FETCH_COLLECTION,
      fetchData: deActions.FETCH_DATA,
      setOutcomeVariables: deActions.SET_OUTCOME_VARIABLES,
    }),
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
      this.setSelectedCohorts(this.tableCohortsSelected);
    },
  },
};
</script>

<style scoped></style>
