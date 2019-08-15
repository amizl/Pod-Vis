<template>
  <v-container v-if="isLoading" fluid fill-height>
    <loading-spinner />
  </v-container>
  <v-container v-else fluid grid-list-md fill-height>
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Cohort Manager</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-flex xs12 sm12> <CohortSelection class="mt-2" /> </v-flex>
      </v-toolbar-items>
      <v-spacer></v-spacer>

      <delete-cohort-button />
      <save-cohort-button />
    </v-toolbar>
    <v-layout column fill-height>
      <v-flex xs6>
        <v-layout fill-height>
          <v-flex xs8> <input-variables /> </v-flex>
          <v-flex xs4> <analytics-table /> </v-flex>
        </v-layout>
      </v-flex>
      <v-flex xs6> <output-variables /> </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState, mapGetters } from 'vuex';
import { actions, state, getters } from '@/store/modules/cohortManager/types';

import CohortSelection from '@/components/CohortManager/CohortSelection.vue';
import AnalyticsTable from '@/components/CohortManager/AnalyticsTable.vue';
import InputVariables from '@/components/CohortManager/InputVariables.vue';
import OutputVariables from '@/components/CohortManager/OutputVariables.vue';
import DeleteCohortButton from '@/components/CohortManager/DeleteCohortBtnDialog';
import SaveCohortButton from '@/components/CohortManager/SaveCohortBtnDialog';

export default {
  name: 'CohortManager',
  components: {
    CohortSelection,
    InputVariables,
    OutputVariables,
    AnalyticsTable,
    SaveCohortButton,
    DeleteCohortButton,
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
    ...mapGetters('cohortManager', {
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
    }),
  },
  async created() {
    this.resetAllStoreData();

    this.isLoading = true;
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    this.isLoading = false;
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCollection: actions.FETCH_COLLECTION,
      fetchData: actions.FETCH_DATA,
      resetAllStoreData: actions.RESET_ALL_STORE_DATA,
    }),
  },
};
</script>

<style scoped></style>
