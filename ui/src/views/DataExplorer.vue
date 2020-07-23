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
    <v-row>
      <v-col cols="12">
        <v-container
          fluid
          fill-width
          class="ma-0 pa-2"
          center="start"
          justify="start"
        >
          <v-app-bar app class="primary">
            <v-icon color="white" large>explore</v-icon>
            <v-toolbar-title class="white--text pl-3"
              >Data Explorer
              <div class="subtitle-1">Dataset: {{ collection.label }}</div>
            </v-toolbar-title>
          </v-app-bar>

          <analysis-tracker
            step="5"
            :substep="substep"
            :collection-id="collectionId"
          ></analysis-tracker>

          <v-container fluid fill-width class="ma-0 pa-0 pt-1">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-sheet color="white" height="100%" class="rounded-lg shadow">
                  <summary-view />
                </v-sheet>
              </v-col>
            </v-row>

            <v-row class="ma-0 pa-0 pt-3">
              <v-col cols="12" class="ma-0 pa-0">
                <v-sheet color="white" height="100%" class="rounded-lg shadow">
                  <cohorts />
                </v-sheet>
              </v-col>
            </v-row>

            <v-row class="ma-0 pa-0 pt-1" min-height="400px">
              <v-col cols="7" class="ma-0 pa-0">
                <v-sheet
                  color="white"
                  height="100%"
                  min-height="400px"
                  class="rounded-lg shadow"
                >
                  <detailed-view min-height="400px" />
                </v-sheet>
              </v-col>

              <v-col cols="5" class="ma-0 pa-0 pl-2">
                <v-sheet color="white" height="100%" class="rounded-lg shadow">
                  <analytics />
                </v-sheet>
              </v-col>
            </v-row>
          </v-container>
        </v-container>
      </v-col>
    </v-row>
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

export default {
  components: {
    AnalysisTracker,
    Analytics,
    SummaryView,
    Cohorts,
    DetailedView,
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
      substep: '5.1',
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
