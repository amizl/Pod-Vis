<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0"> <loading-spinner /> </v-col>
    </v-row>
  </v-container>

  <div v-else fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>library_add</v-icon>
      <v-toolbar-title class="white--text pl-2"
        >Create New Study Dataset - Choose First & Last Visit
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
        </div>
      </v-toolbar-title>
      <v-spacer></v-spacer>

      <v-chip
        v-if="useAutomatedAnalysisMode"
        color="yellow"
        text-color="black"
        class="mr-1"
        :disabled="!useAutomatedAnalysisMode"
        >Auto Mode ON</v-chip
      >

      <save-first-last-visit-btn-dialog
        ref="save_visits"
        :disabled="useAutomatedAnalysisMode"
        :use-long-scale-names="useLongScaleNames"
      />
    </v-app-bar>

    <analysis-tracker
      step="1"
      :substep="substep"
      :collection-id="collection.id"
    ></analysis-tracker>

    <v-container fluid fill-width class="ma-0 pa-0 pt-2">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-sheet
            color="white"
            height="100%"
            class="rounded-lg shadow ma-0 pa-0"
          >
            <visit-variables-toolbar
              class="ma-0 pa-0"
              @hideUnselectedVars="hideUnselectedVarsChanged"
              @useLongScaleNames="useLongScaleNamesChanged"
            >
            </visit-variables-toolbar>

            <visit-times-table></visit-times-table>

            <bubble-chart
              ref="bubble_chart"
              :var-opacity="'0.3'"
              :collection-var-opacity="'0.8'"
              :hide-unselected-vars="hideUnselectedVars"
              :use-long-scale-names="useLongScaleNames"
            >
            </bubble-chart>
            <v-spacer></v-spacer>
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog
      v-model="aaDialog"
      persistent
      scrollable
      max-width="50%"
      min-height="50%"
    >
      <v-card class="rounded-lg" style="border: 3px solid #3f51b5;">
        <v-card-title color="white" class="ma-0 pa-2" primary-title>
          <span class="primary--text text--darken-3 title"
            >Automated Analysis Mode: Set Visits</span
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
                <!--
	      <v-progress-linear v-if="i == aaProgress"
				   indeterminate
					      color="primary"
					      class="pt-2"
				   ></v-progress-linear> -->
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
            @click="aaToCohortManager()"
          >
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataSummary/types';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import VisitVariablesToolbar from '@/components/DataSummary/VisitVariablesToolbar.vue';
import VisitTimesTable from '@/components/DataSummary/VisitTimesTable.vue';
import BubbleChart from '@/components/DataSummary/BubbleChart/BubbleChart.vue';
import SaveFirstLastVisitBtnDialog from '@/components/BuildDataset/SaveFirstLastVisitBtnDialog.vue';
import {
  getObservationVariableIds,
  getCollectionDescription,
  estimateMaxSubjects,
} from '@/utils/helpers';

var aaSteps = [
  { title: 'Loading visit data' },
  { title: 'Setting first and last visits' },
  { title: 'Saving first and last visits' },
  { title: 'Done' },
];

export default {
  name: 'DataSummary',
  components: {
    AnalysisTracker,
    VisitVariablesToolbar,
    VisitTimesTable,
    BubbleChart,
    SaveFirstLastVisitBtnDialog,
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
    aaWhichOutcomes: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      isLoading: false,
      substep: '1.4',
      hideUnselectedVars: true,
      getCollectionDescription: getCollectionDescription,
      useLongScaleNames: false,
      aaDialog: false,
      aaProgress: 0,
      aaLastUpdate: null,
      aaMinStepTime: 1,
      aaSteps: aaSteps,
    };
  },
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      collection_summaries: state.COLLECTION_SUMMARIES,
      firstVisits: state.FIRST_VISITS,
      lastVisits: state.LAST_VISITS,
    }),
    useAutomatedAnalysisMode() {
      return this.aaPredictors.length + this.aaOutputs.length > 0;
    },
  },
  async created() {
    this.isLoading = true;
    if (this.useAutomatedAnalysisMode) {
      this.aaDialog = true;
      this.aaProgress = 0;
    }
    await this.fetchCollection(this.collectionId);
    await this.fetchCollectionSummaries(this.collectionId);
    this.isLoading = false;
    if (this.useAutomatedAnalysisMode) {
      this.doAutomatedAnalysis();
    }
  },
  methods: {
    ...mapActions('dataSummary', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchCollectionSummaries: actions.FETCH_COLLECTION_SUMMARIES,
    }),
    hideUnselectedVarsChanged(newval) {
      this.hideUnselectedVars = newval;
    },
    useLongScaleNamesChanged(newval) {
      this.useLongScaleNames = newval;
    },
    fetchSubjectVariableVisits() {
      const base = `/api/studies/subject_variable_visits`;
      const query = this.collection.studies
        .map(({ study_id }) => `id=${study_id}`)
        .join('&');
      return axios.get(`${base}?${query}`);
    },
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

      // get subject visit info
      const { data: subjVarVisits } = await this.fetchSubjectVariableVisits();
      this.subject_variable_visits = subjVarVisits['visits'];

      await this.updateAutomatedAnalysisProgress(1);

      // compute first/last visits
      var varIds = getObservationVariableIds(this.collection);
      var ems = estimateMaxSubjects(
        this.subject_variable_visits,
        varIds,
        'event'
      );

      // set first and last visits
      var events = this.subject_variable_visits['visits']['event'];

      ems['visits'].forEach(vis => {
        this.firstVisits[vis[0]] = events[vis[1]]['visit_event'];
        this.lastVisits[vis[0]] = events[vis[2]]['visit_event'];
      });

      // move visit handles to agree with consensus
      this.$refs.bubble_chart.setVisitHandle(true);
      this.$refs.bubble_chart.setVisitHandle(false);

      // save first and last visits
      await this.updateAutomatedAnalysisProgress(2);
      await this.$refs.save_visits.saveVisits();

      await this.updateAutomatedAnalysisProgress(3);
      await this.updateAutomatedAnalysisProgress(4);
    },
    // continue to Cohort Manager
    aaToCohortManager() {
      var query = { collection: this.collection.id };
      if (this.useAutomatedAnalysisMode) {
        query['aa_predictors'] = this.aaPredictors;
        query['aa_outputs'] = this.aaOutputs;
        query['aa_ranges'] = this.aaRanges;
        query['aa_mcs'] = this.aaMCS;
        query['aa_which_outcomes'] = this.aaWhichOutcomes;
      }
      this.$router.push({ name: 'cohortManager', query: query });
    },
  },
};
</script>
