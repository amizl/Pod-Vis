<template>
  <v-container v-if="isLoading" fluid fill-height>
    <loading-spinner />
  </v-container>
  <v-container v-else fluid grid-list-md fill-height>
    <v-toolbar extended app class="primary shadow send-to-back">
      <v-toolbar-title class="white--text">Cohort Manager</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items> <CohortSelection class="mt-3" /> </v-toolbar-items>
      <v-spacer></v-spacer>
      <v-btn color="primary--text">Save Cohort</v-btn>
    </v-toolbar>
    <v-layout d-block class="translate-up" fill-height>
      <v-flex fill-height xs12>
        <v-layout column fill-height>
          <v-flex xs5 fill-height>
            <v-layout row fill-height>
              <v-flex xs8> <input-variables /> </v-flex>
              <v-flex xs4> <analytics-table /> </v-flex>
            </v-layout>
          </v-flex>
          <v-flex> <output-variables /> </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';

import CohortSelection from '@/components/CohortManager/CohortSelection.vue';
import AnalyticsTable from '@/components/CohortManager/AnalyticsTable.vue';
import InputVariables from '@/components/CohortManager/InputVariables.vue';
import OutputVariables from '@/components/CohortManager/OutputVariables.vue';

export default {
  name: 'CohortManager',
  components: {
    CohortSelection,
    InputVariables,
    OutputVariables,
    AnalyticsTable,
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
    };
  },
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
    }),
  },
  async created() {
    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    this.isLoading = false;
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchData: actions.FETCH_DATA,
    }),
  },
};
</script>

<style scoped></style>
