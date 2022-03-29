><template>
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
            class="rounded-lg shadow ma-0 pa-0 pb-2"
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

            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <v-btn
                  class="primary text--white ma-0 ml-2 px-2 py-0"
                  v-on="{ ...tooltip }"
                  @click="autoSetVisits"
                  >Auto Set Visits</v-btn
                >
              </template>
              <span class="subtitle-1"
                >Automatically set first and last visit for all variables.</span
              >
            </v-tooltip>
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>

    <v-dialog
      v-model="autoSetDialog"
      persistent
      scrollable
      max-width="50%"
      min-height="50%"
    >
      <v-card class="rounded-lg" style="border: 3px solid #3f51b5;">
        <v-card-title color="white" class="ma-0 pa-2" primary-title>
          <span class="primary--text text--darken-3 title"
            >Automatically Set First & Last Visits</span
          >
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="py-4">
          <v-list>
            <v-list-item v-for="(s, i) in autoSetSteps" :key="`as-${i}`">
              <v-list-item-content> {{ s.title }} </v-list-item-content>
              <v-list-item-avatar>
                <v-icon v-if="i < autoSetSteps.length - 1">done</v-icon>
              </v-list-item-avatar>
            </v-list-item>
          </v-list>

          <v-container v-if="autoSetEstMaxStudySize">
            <v-row>
              <v-col cols="10">
                <v-slider
                  v-model="autoSetMinStudySize"
                  class="pt-3"
                  label="Minimum study population size"
                  step="1"
                  thumb-label="always"
                  min="1"
                  :max="autoSetEstMaxStudySize"
                  @change="doAutoSet(autoSetMinStudySize)"
                >
                </v-slider>
              </v-col>

              <v-col cols="2">
                <v-text-field
                  v-model.number="autoSetMinStudySize"
                  class="center-text pa-0 ma-0"
                  type="number"
                  @change="doAutoSet(autoSetMinStudySize)"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-row class="ma-0 pa-0">
              <v-col cols="12"  class="ma-0 pa-0">
		Move the slider above until the study population size and average elapsed time (from the selected first visit to last visit) shown below are acceptable and then click on "SET VISITS":
	      </v-col>
	    </v-row>
	    
            <v-row>
              <v-col>
                <v-chip
                  class="title ml-3"
                  :color="getNumSubjectsColor(numSelectedSubjects)"
                  :text-color="getNumSubjectsTextColor(numSelectedSubjects)"
                  >Study Population - {{ numSelectedSubjects }}</v-chip
                >

                <v-chip class="title ml-3" color="deep-orange lighten-4"
                  >Average Elapsed Time -
                  {{ avgTimeBetweenVisits | formatTime }}
                </v-chip>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            class="primary white--text ma-0 px-2 mx-2"
            :disabled="!autoSetEnableCloseDialog"
            @click="closeAutoSetDialog()"
          >
            SET VISITS
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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

        <v-card-actions v-if="aaDialogOKButton">
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
import { format } from 'd3-format';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import VisitVariablesToolbar from '@/components/DataSummary/VisitVariablesToolbar.vue';
import VisitTimesTable from '@/components/DataSummary/VisitTimesTable.vue';
import BubbleChart from '@/components/DataSummary/BubbleChart/BubbleChart.vue';
import SaveFirstLastVisitBtnDialog from '@/components/BuildDataset/SaveFirstLastVisitBtnDialog.vue';
import {
  colors,
  getNumSubjectsColor,
  getNumSubjectsTextColor,
} from '@/utils/colors';
import {
  getObservationVariableIds,
  getCollectionDescription,
  estimateMaxSubjects,
  estimateMaxVisits,
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
  filters: {
    formatTime(tsecs) {
      var tdays = tsecs / (3600 * 24);
      var tyears = tdays / 365.25;
      if (tdays <= 60) {
        return format('.1f')(tdays) + ' days';
      } else {
        return format('.1f')(tyears) + ' year(s)';
      }
    },
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
      aaDialogOKButton: false,
      // auto-set feature
      autoSetDialog: false,
      autoSetEnableCloseDialog: false,
      autoSetEnableSetButton: false,
      autoSetSteps: [],
      autoSetEstMaxStudySize: null,
      autoSetMinStudySize: 1,
      autoSetDefaultFrac: 0.7,
      aaProgress: 0,
      aaLastUpdate: null,
      aaMinStepTime: 1,
      aaSteps: aaSteps,
      subject_variable_visits: null,
      colors: colors,
      getNumSubjectsColor: getNumSubjectsColor,
      getNumSubjectsTextColor: getNumSubjectsTextColor,
      avgTimeBetweenVisits: null,
    };
  },
  watch: {
    timesBetweenVisits(tbv) {
      if (tbv != null) {
        let self = this;
        tbv.forEach(t => {
          if (t['study_name'] == '_all') {
            self.avgTimeBetweenVisits = t['avg_time_secs'];
          }
        });
      }
    },
  },
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      collection_summaries: state.COLLECTION_SUMMARIES,
      firstVisits: state.FIRST_VISITS,
      lastVisits: state.LAST_VISITS,
      numSelectedSubjects: state.NUM_SELECTED_SUBJECTS,
      timesBetweenVisits: state.TIMES_BETWEEN_VISITS,
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
      this.doAutomatedAnalysisPreVisits();
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
    // automated analysis mode before first/last visits have been set
    async doAutomatedAnalysisPreVisits() {
      await this.updateAutomatedAnalysisProgress(0);
      // get subject visit info
      const { data: subjVarVisits } = await this.fetchSubjectVariableVisits();
      this.subject_variable_visits = subjVarVisits['visits'];
      await this.updateAutomatedAnalysisProgress(1);
      this.aaDialog = false;
      await this.autoSetVisits();
    },
    // automated analysis mode after first/last visits have been set
    async doAutomatedAnalysisPostVisits() {
      // save first and last visits
      await this.updateAutomatedAnalysisProgress(2);
      await this.$refs.save_visits.saveVisits();

      await this.updateAutomatedAnalysisProgress(3);
      await this.updateAutomatedAnalysisProgress(4);
      if (!this.aaDialogOKButton) {
        await this.sleep(2000);
        this.aaToCohortManager();
      }
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
    async doAutoSet(min_size) {
      var varIds = getObservationVariableIds(this.collection);
      var emv = estimateMaxVisits(
        this.subject_variable_visits,
        varIds,
        'event',
        min_size
      );

      // set first and last visits
      var events = this.subject_variable_visits['visits']['event'];

      emv['visits'].forEach(vis => {
        this.firstVisits[vis[0]] = events[vis[1]]['visit_event'];
        this.lastVisits[vis[0]] = events[vis[2]]['visit_event'];
      });

      // move visit handles to agree with consensus
      this.$refs.bubble_chart.setVisitHandle(true);
      this.$refs.bubble_chart.setVisitHandle(false);
      //      let study_count = emv['counts']['all'];
      //      this.autoSetSteps.push({ 'title': "Study population for auto-selected first/last visit with size >= " + min_size + ": " + study_count });
      this.autoSetEnableCloseDialog = true;
    },
    async autoSetVisits() {
      this.autoSetSteps = [];
      this.autoSetDialog = true;

      // get subject visit info
      if (!this.subject_variable_visits) {
        this.autoSetSteps.push({ title: 'Loading subject visit data' });
        const { data: subjVarVisits } = await this.fetchSubjectVariableVisits();
        this.subject_variable_visits = subjVarVisits['visits'];
      }

      // run standard routine to get estimate of the max possible study dataset size
      var varIds = getObservationVariableIds(this.collection);
      var ems = estimateMaxSubjects(
        this.subject_variable_visits,
        varIds,
        'event'
      );

      this.autoSetSteps.push({
        title:
          'Estimated maximum study population size for the selected variables: ' +
          ems['counts']['all'],
      });

      this.autoSetEstMaxStudySize = ems['counts']['all'];

      // compute minimum number of subjects as fraction of total
      var defaultMinSubjects = Math.round(this.autoSetDefaultFrac * ems['counts']['all']);

      this.autoSetSteps.push({
        title: 'Setting minimum study population size to ' + (this.autoSetDefaultFrac * 100) + '% of estimated maximum: ' + defaultMinSubjects,
      });
      this.autoSetMinStudySize = defaultMinSubjects;
      this.doAutoSet(defaultMinSubjects);

      this.autoSetSteps.push({
        title: 'Select desired minimum study population size: ',
      });
    },
    async closeAutoSetDialog() {
      this.autoSetDialog = false;
      // continue with automated analysis mode
      if (this.useAutomatedAnalysisMode) {
        this.aaDialog = true;
        this.doAutomatedAnalysisPostVisits();
      }
    },
  },
};
</script>
