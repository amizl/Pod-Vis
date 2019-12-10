<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <loading-spinner />
  </v-container>
  <v-container v-else fluid grid-list-md fill-height class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Analysis Summary
        <div class="subheading">{{ collection.label }}</div>
      </v-toolbar-title>
    </v-toolbar>

    <v-layout column fill-height class="ma-0 pa-0">
      <one-way-anova-grid />
      <tukey-hsd-grid class="mt-2" />
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions } from '@/store/modules/analysisSummary/types';
import {
  actions as deActions,
  state as deState,
} from '@/store/modules/dataExplorer/types';

import OneWayAnovaGrid from '@/components/AnalysisSummary/OneWayANOVAGrid.vue';
import TukeyHsdGrid from '@/components/AnalysisSummary/TukeyHSDGrid.vue';

export default {
  name: 'AnalysisSummary',
  components: {
    OneWayAnovaGrid,
    TukeyHsdGrid,
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
