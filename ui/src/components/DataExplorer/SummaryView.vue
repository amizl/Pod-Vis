<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <summary-view-toolbar></summary-view-toolbar>
      <v-container fluid fill-height class="pa-0 pl-3">
        <summary-parallel-coordinates v-if="userAddedOutcomeVariables" />
        <v-layout v-else column align-center justify-center fill-height>
          <v-subheader class="display-1 primary--text text--lighten-5">
            ADD OUTCOME VARIABLES
          </v-subheader>
        </v-layout>
      </v-container>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';
import SummaryParallelCoordinates from '@/components/DataExplorer/SummaryParallelCoordinates.vue';
import SummaryViewToolbar from '@/components/DataExplorer/SummaryViewToolbar.vue';

export default {
  components: {
    SummaryParallelCoordinates,
    SummaryViewToolbar,
  },
  data() {
    return {};
  },
  computed: {
    ...mapState('dataExplorer', {
      outcomeVariables: state.OUTCOME_VARIABLES,
    }),
    userAddedOutcomeVariables() {
      return this.outcomeVariables.length > 0;
    },
  },
};
</script>

<style scoped></style>
