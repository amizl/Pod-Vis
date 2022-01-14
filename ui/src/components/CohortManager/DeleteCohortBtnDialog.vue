<template>
  <div>
    <v-btn
      :disabled="!hasUserSelectedCohort"
      color="error"
      @click="dialog = !dialog"
    >
      <v-icon left>delete</v-icon> DELETE STUDY GROUP
    </v-btn>
    <!-- DELETE COHORT FORM DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title color="white" primary-title>
          <v-icon color="primary">delete</v-icon>
          <span class="primary--text text--darken-3 title pl-2"
            >Delete Study Group</span
          >
        </v-card-title>

        <v-card-text class="primary primary--text text--lighten-5 pt-4">
          Are you sure you want to delete this study group?
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn :loading="loading" color="error" @click="onDeleteCohort">
            <v-icon color="" left>delete</v-icon> Delete Study Group</v-btn
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
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
  },
  methods: {
    ...mapActions('cohortManager', {
      deleteSelectedCohort: actions.DELETE_SELECTED_COHORT,
    }),
    async onDeleteCohort() {
      try {
        await this.deleteSelectedCohort();
        this.loading = false;
        this.dialog = false;
        this.$emit('cohortDeleted', true);
      } catch (err) {
        this.loading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
