<template>
  <div>
    <v-btn
      class="primary text--white ma-0 px-2 py-0"
      :disabled="!hasUserFilteredInputVariables"
      @click="dialog = !dialog"
    >
      Save Cohort
    </v-btn>
    <!-- SAVE COLLECTION FORM DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title color="white" primary-title>
          <v-icon color="primary">save</v-icon>
          <span class="primary--text text--darken-3 title pl-2"
            >Save Cohort</span
          >
        </v-card-title>

        <v-card-text class="primary primary--text text--lighten-5 pt-4">
          <div
            v-if="hasUserFilteredOutputVariables"
            class="red--text text--lighten-4 title pl-2 py-4"
          >
            WARNING:<br clear="both" />Outcome variable filters will not be
            saved with the cohort unless they are moved to the PREDICTOR
            VARIABLES section.<br clear="both" />
          </div>

          <v-form
            ref="form"
            v-model="valid"
            class="white"
            @submit.prevent="onSaveCohort"
          >
            <v-text-field
              ref="vtf"
              v-model="cohortName"
              :rules="[
                () => !!cohortName || 'Cohort name is required.',
                () =>
                  !cohortNames.includes(cohortName) ||
                  'A cohort with that name already exists.',
              ]"
              prepend-inner-icon="table_chart"
              label="Please name your cohort."
              filled
              text
              background-color="grey lighten-4"
              class="mt-2"
            >
            </v-text-field>
          </v-form>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn :loading="loading" color="primary" @click="onSaveCohort">
            <v-icon left>save</v-icon> Save Cohort</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import { actions, getters, state } from '@/store/modules/cohortManager/types';

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
    cohorts: {
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
    ...mapState('cohortManager', {
      cohort: state.COHORT,
    }),
    ...mapGetters('cohortManager', {
      hasUserFilteredInputVariables: getters.HAS_USER_FILTERED_INPUT_VARIABLES,
      hasUserFilteredOutputVariables:
        getters.HAS_USER_FILTERED_OUTPUT_VARIABLES,
    }),
    cohortNames() {
      return this.cohorts.map(c => c.label);
    },
  },
  watch: {
    dialog(val) {
      if (val) {
        this.showing();
      }
    },
    cohort(newCohort) {
      if (
        newCohort.label != 'Choose Cohort' &&
        newCohort.label != 'New Cohort'
      ) {
        this.cohortName = newCohort.label;
      }
    },
  },
  methods: {
    ...mapActions('cohortManager', {
      saveSelectedCohort: actions.SAVE_SELECTED_COHORT,
    }),
    showing() {
      setTimeout(() => {
        this.$refs.vtf.focus();
      });
    },
    async onSaveCohort() {
      const { cohortName } = this;
      if (this.$refs.form.validate()) {
        this.loading = true;
        try {
          await this.saveSelectedCohort({ cohortName });
          this.loading = false;
          this.dialog = false;
          this.$emit('cohortSaved', true);
        } catch (err) {
          this.loading = false;
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
