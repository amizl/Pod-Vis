<template>
  <v-container v-if="isLoading" fluid fill-height>
    <loading-spinner />
  </v-container>
  <v-container v-else fluid fill-height grid-list-md>
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Data Explorer</v-toolbar-title>
    </v-toolbar>
    <v-layout column fill-height>
      <v-flex>
        <v-layout fill-height>
          <v-flex xs3> <outcome-variables /></v-flex>
          <v-flex xs9> <summary-view /> </v-flex>
        </v-layout>
      </v-flex>
      <v-flex>
        <v-layout fill-height>
          <v-flex xs3> <cohorts /> </v-flex>
          <v-flex xs9> <detailed-view /> </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import OutcomeVariables from '@/components/DataExplorer/OutcomeVariables.vue';
import SummaryView from '@/components/DataExplorer/SummaryView.vue';
import Cohorts from '@/components/DataExplorer/Cohorts.vue';
import DetailedView from '@/components/DataExplorer/DetailedView.vue';

export default {
  components: {
    OutcomeVariables,
    SummaryView,
    Cohorts,
    DetailedView,
  },
  data() {
    return {
      isLoading: false,
    };
  },
  created() {},
};
</script>

<style scoped></style>
