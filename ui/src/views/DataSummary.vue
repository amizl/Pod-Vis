<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <loading-spinner />
  </v-container>
  <v-container v-else fluid fill-width class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-icon color="white" large>library_add</v-icon>
      <v-toolbar-title class="white--text"
        >Create New Study Dataset - Choose First & Last Visit
        <div class="subheading">Dataset: {{ collection.label }}</div>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <save-first-last-visit-btn-dialog />
    </v-toolbar>

    <v-layout row class="ma-0 pa-0">
      <v-flex xs12>
        <analysis-tracker step="2" :substep="substep"></analysis-tracker>
      </v-flex>
    </v-layout>

    <v-layout fill-width class="mt-2 pa-0">
      <v-flex xs12>
        <v-sheet color="white" height="100%" class="rounded-lg shadow">
          <v-layout column class="ma-1 pt-1">
            <visit-variables-toolbar
              @hideUnselectedVars="hideUnselectedVarsChanged"
            >
            </visit-variables-toolbar>

            <v-container fluid fill-height class="pa-0 pb-0">
              <bubble-chart
                :var-opacity="'0.3'"
                :collection-var-opacity="'0.8'"
                :hide-unselected-vars="hideUnselectedVars"
              >
              </bubble-chart>
              <v-spacer></v-spacer>
            </v-container>

            <visit-times-table></visit-times-table>
          </v-layout>
        </v-sheet>
      </v-flex>
    </v-layout>
  </v-container>
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
