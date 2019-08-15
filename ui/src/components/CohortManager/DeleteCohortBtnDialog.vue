<template>
  <div>
    <v-btn
      :disabled="!hasUserFilteredInputVariables"
      flat
      outline
      color="error"
      @click="dialog = !dialog"
    >
      <v-icon color="error" left>delete</v-icon> DELETE COHORT
    </v-btn>
    <!-- DELETE COHORT FORM DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title primary-title>
          <span class="primary--text title pl-2"
            >Are you sure you want to delete this cohort?</span
          >
        </v-card-title>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="red lighten-2" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn :loading="loading" color="primary" @click="onDeleteCohort">
            <v-icon color="" left>delete</v-icon> Delete Cohort</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { actions, getters } from '@/store/modules/cohortManager/types';

// which store?
export default {
  props: {
    variables: {
      type: Array,
      default: () => [],
    },
    datasetIds: {
      type: Array,
      default: () => [],
    },
  },
  data: () => ({
    cohortName: '',
    valid: true,
    dialog: false,
    loading: false,
  }),
  computed: {
    ...mapGetters('cohortManager', {
      hasUserFilteredInputVariables: getters.HAS_USER_FILTERED_INPUT_VARIABLES,
    }),
  },
  methods: {
    ...mapActions('cohortManager', {
      saveCohort: actions.SAVE_COHORT,
      deleteSelectedCohort: actions.DELETE_SELECTED_COHORT,
    }),
    async onDeleteCohort() {
      try {
        await this.deleteSelectedCohort();
        this.loading = false;
        this.dialog = false;
      } catch (err) {
        this.loading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
