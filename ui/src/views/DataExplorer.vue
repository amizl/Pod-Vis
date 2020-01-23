<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-1">
    <loading-spinner />
  </v-container>
  <v-container v-else fluid fill-width class="ma-0 pa-1">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Data Explorer
        <div class="subheading">{{ collection.label }}</div>
      </v-toolbar-title>
      <v-spacer />
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
          step="4"
          :substep="substep"
          :collection-id="collectionId"
        ></analysis-tracker>
      </v-flex>
    </v-layout>

    <v-layout row fill-height class="ma-0 pa-0">
      <v-flex xs12> <summary-view /> </v-flex>
    </v-layout>

    <v-layout row fill-height class="ma-0 pa-0">
      <v-flex fill-height xs12>
        <v-layout col fill-height class="ma-0 pa-0">
          <v-flex xs3 fill-height class="ma-0 pa-1"> <cohorts /> </v-flex>
          <v-flex xs6 fill-height class="ma-0 pa-1"> <detailed-view /> </v-flex>
          <v-flex xs3 fill-height class="ma-0 pa-1"> <analytics /> </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
    <!--
    <v-layout column fill-height>
      <v-flex xs7 class="ma-0 pa-1">
        <v-layout fill-height>
          <v-flex xs3 fill-height>
            <v-layout column fill-height>

            </v-layout>
          </v-flex>

          <v-flex xs3 class="ma-0 pa-1">
            <v-layout column fill-height>

            </v-layout>
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
-->
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import SummaryView from '@/components/DataExplorer/SummaryView.vue';
import Cohorts from '@/components/DataExplorer/Cohorts.vue';
import Analytics from '@/components/DataExplorer/Analytics.vue';
import DetailedView from '@/components/DataExplorer/DetailedView.vue';
import AnalysisSummaryButton from '@/components/DataExplorer/AnalysisSummaryBtnDialog';

export default {
  components: {
    AnalysisTracker,
    Analytics,
    SummaryView,
    Cohorts,
    DetailedView,
    AnalysisSummaryButton,
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
    cohortIds: {
      type: String,
      required: false,
      default: undefined,
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
      cohorts: state.COHORTS,
      collection: state.COLLECTION,
      outcomeVariables: state.OUTCOME_VARIABLES,
    }),
  },
  async created() {
    // this.resetAllStoreData();
    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    await this.fetchCohorts();
    this.isLoading = false;

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
    this.setOutcomeVariables(outcomeVars);

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

    // initialize page with preselected list of cohorts displayed in detailed view
    if (typeof this.cohortIds !== 'undefined' && this.cohortIds !== '') {
      const cids = this.cohortIds.split(',');
      const cidD = {};
      cids.forEach(cid => {
        cidD[cid] = 1;
      });
      const vc = [];
      this.cohorts.forEach(c => {
        if (c.id in cidD) {
          vc.push(c);
        }
      });
      this.setVisibleCohorts(vc);
    }
  },
  methods: {
    ...mapActions('dataExplorer', {
      fetchCohorts: actions.FETCH_COHORTS,
      fetchCollection: actions.FETCH_COLLECTION,
      fetchData: actions.FETCH_DATA,
      setOutcomeVariables: actions.SET_OUTCOME_VARIABLES,
      setDetailedView: actions.SET_DETAILED_VIEW,
      setVisibleCohorts: actions.SET_VISIBLE_COHORTS,
    }),
  },
};
</script>

<style scoped></style>
