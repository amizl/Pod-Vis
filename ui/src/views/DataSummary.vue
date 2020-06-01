<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-2">
    <loading-spinner />
    <span>Loading ... {{ collection.label }} </span>
  </v-container>
  <v-container v-else fluid fill-width>
    <v-toolbar app class="primary">
      <v-toolbar-title class="subheading white--text"
        >Data Summary Viewer
        <div class="subheading">{{ collection.label }}</div>
      </v-toolbar-title>
      <v-spacer></v-spacer>

      <v-tooltip top color="primary">
        <span>View Data Summary</span>
      </v-tooltip>
    </v-toolbar>
    <v-layout>
      <v-flex>
        <analysis-tracker step="3" :substep="substep"></analysis-tracker>
      </v-flex>
    </v-layout>

    <v-layout fill-height>
      <v-flex> <visit-variables /> </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataSummary/types';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import VisitVariables from '@/components/DataSummary/VisitVariables.vue';

export default {
  name: 'DataSummary',
  components: {
    AnalysisTracker,
    VisitVariables,
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
      substep: '3.1',
    };
  },
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      collection_summary: state.COLLECTION_SUMMARY,
    }),
  },
  async created() {
    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchCollectionSummaryByEvent(this.collectionId);
    this.isLoading = false;
  },
  methods: {
    ...mapActions('dataSummary', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchCollectionSummaryByEvent: actions.FETCH_COLLECTION_SUMMARY_BY_EVENT,
    }),
  },
};
</script>