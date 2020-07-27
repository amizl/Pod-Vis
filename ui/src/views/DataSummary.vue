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
        <div class="subtitle-1">Dataset: {{ collection.label }}</div>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <save-first-last-visit-btn-dialog />
    </v-app-bar>

    <analysis-tracker
      step="2"
      :substep="substep"
      :collection-id="this.collection.id"
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
            >
            </visit-variables-toolbar>

            <bubble-chart
              :var-opacity="'0.3'"
              :collection-var-opacity="'0.8'"
              :hide-unselected-vars="hideUnselectedVars"
            >
            </bubble-chart>
            <v-spacer></v-spacer>

            <visit-times-table></visit-times-table>
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataSummary/types';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import VisitVariablesToolbar from '@/components/DataSummary/VisitVariablesToolbar.vue';
import VisitTimesList from '@/components/DataSummary/VisitTimesList.vue';
import VisitTimesTable from '@/components/DataSummary/VisitTimesTable.vue';
import BubbleChart from '@/components/DataSummary/BubbleChart/BubbleChart.vue';
import SaveFirstLastVisitBtnDialog from '@/components/BuildDataset/SaveFirstLastVisitBtnDialog.vue';

export default {
  name: 'DataSummary',
  components: {
    AnalysisTracker,
    VisitVariablesToolbar,
    VisitTimesList,
    VisitTimesTable,
    BubbleChart,
    SaveFirstLastVisitBtnDialog,
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
      substep: '2.4',
      hideUnselectedVars: true,
    };
  },
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      collection_summaries: state.COLLECTION_SUMMARIES,
    }),
  },
  async created() {
    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchCollectionSummaries(this.collectionId);
    this.isLoading = false;
  },
  methods: {
    ...mapActions('dataSummary', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchCollectionSummaries: actions.FETCH_COLLECTION_SUMMARIES,
    }),
    hideUnselectedVarsChanged(newval) {
      this.hideUnselectedVars = newval;
    },
  },
};
</script>
