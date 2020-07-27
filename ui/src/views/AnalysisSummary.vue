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
    </v-app-bar>

    <analysis-tracker
      step="4"
      :substep="substep"
      :collection-id="collectionId"
    ></analysis-tracker>

    <v-container fluid fill-width class="ma-0 pa-0 pt-2">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0"> <cohort-table /> </v-col>
      </v-row>

      <v-row class="ma-0 pa-0 mt-2">
        <v-col cols="6" class="ma-0 pa-0"> <one-way-anova-grid /> </v-col>

        <v-col cols="6" class="ma-0 pa-0 pl-2"> <tukey-hsd-grid /> </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions } from '@/store/modules/analysisSummary/types';
import {
  actions as deActions,
  state as deState,
} from '@/store/modules/dataExplorer/types';

import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import OneWayAnovaGrid from '@/components/AnalysisSummary/OneWayANOVAGrid.vue';
import TukeyHsdGrid from '@/components/AnalysisSummary/TukeyHSDGrid.vue';
import CohortTable from '@/components/common/CohortTable.vue';

export default {
  name: 'AnalysisSummary',
  components: {
    AnalysisTracker,
    OneWayAnovaGrid,
    TukeyHsdGrid,
    CohortTable,
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
      substep: '4.1',
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      cohorts: deState.COHORTS,
      collection: deState.COLLECTION,
      data: deState.DATA,
      outcomeVariables: deState.OUTCOME_VARIABLES,
    }),
  },
  async created() {
    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    await this.fetchCohorts();

    // set outcome variables to union of cohorts' output variables
    const varsAdded = {};
    const outcomeVars = [];
    this.cohorts
      .filter(v => v.collection_id === this.collectionId)
      .forEach(c => {
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
      cohorts: this.cohorts,
      data: this.data,
    });
    this.isLoading = false;
  },
  methods: {
    ...mapActions('analysisSummary', {
      analyzeCohorts: actions.ANALYZE_COHORTS,
    }),
    ...mapActions('dataExplorer', {
      fetchCohorts: deActions.FETCH_COHORTS,
      fetchCollection: deActions.FETCH_COLLECTION,
      fetchData: deActions.FETCH_DATA,
      setOutcomeVariables: deActions.SET_OUTCOME_VARIABLES,
    }),
  },
};
</script>

<style scoped></style>
