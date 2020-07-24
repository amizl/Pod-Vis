<template>
  <div class="ma-1">
    <v-app-bar dense text class="rounded-lg">
      <v-toolbar-title class="primary--text title">
        Choose Outcome Variable
      </v-toolbar-title>
      <v-spacer />
    </v-app-bar>

    <v-container fluid fill-height class="pa-0 pl-3 pt-3">
      <span>Variable:</span>
      <v-btn-toggle v-model="dview" class="pl-2" mandatory>
        <v-btn
          v-for="v in outcomeVariables"
          text
          color="primary"
          class="white--text"
          :value="v"
          >{{ v.label }}</v-btn
        >
      </v-btn-toggle>
    </v-container>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/dataExplorer/types';
import SummaryParallelCoordinates from '@/components/DataExplorer/SummaryParallelCoordinates.vue';
import SummaryViewToolbar from '@/components/DataExplorer/SummaryViewToolbar.vue';

export default {
  components: {
    SummaryParallelCoordinates,
    SummaryViewToolbar,
  },
  data() {
    return {
      dview: null,
    };
  },
  watch: {
    dview(newval) {
      this.setDetailedView(newval);
    },
  },
  mounted() {
    if (this.detailedView == null) {
      if (this.dview != null) {
        this.setDetailedView(this.dview);
      }
    } else {
      this.dview = this.detailedView;
    }
  },
  computed: {
    ...mapState('dataExplorer', {
      detailedView: state.DETAILED_VIEW,
      outcomeVariables: state.OUTCOME_VARIABLES,
      collection: state.COLLECTION,
    }),
    userAddedOutcomeVariables() {
      return this.outcomeVariables.length > 0;
    },
  },
  methods: {
    ...mapActions('dataExplorer', {
      setDetailedView: actions.SET_DETAILED_VIEW,
    }),
  },
};
</script>

<style scoped></style>
