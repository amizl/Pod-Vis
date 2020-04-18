<template>
  <div>
    <v-btn
      :disabled="!hasUserFilteredInputVariables"
      color="primary--text"
      @click="dialog = !dialog"
    >
      <v-icon left>save</v-icon> SAVE COHORT
    </v-btn>
    <!-- SAVE COLLECTION FORM DIALOG -->
    <v-dialog v-model="dialog" width="500" persistent>
      <v-card class="rounded-lg">
        <v-card-title primary-title>
          <span class="primary--text title pl-2">Save Cohort</span>

          <span
            v-if="hasUserFilteredOutputVariables"
            class="red--text title pl-2 pt-4"
          >
            WARNING:<br clear="both" /><br clear="both" />Outcome variable
            filters will not be saved with the cohort unless they are moved to
            the INPUT VARIABLES section.
          </span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="onSaveCohort">
            <v-text-field
              ref="vtf"
              v-model="cohortName"
              :rules="[() => !!cohortName || 'Cohort name is required.']"
              prepend-inner-icon="table_chart"
              label="Please name your cohort."
              box
              flat
              background-color="grey lighten-4"
              class="mt-2"
              hide-details
            >
            </v-text-field>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="red lighten-2" @click="dialog = false">
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
      hasUserFilteredOutputVariables: getters.HAS_USER_FILTERED_OUTPUT_VARIABLES,
    }),
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
      saveCohort: actions.SAVE_COHORT,
    }),
    showing() {
      this.$nextTick(function() {
        this.$refs.vtf.focus();
      });
    },
    async onSaveCohort() {
      const { cohortName } = this;
      if (this.$refs.form.validate()) {
        this.loading = true;
        try {
          await this.saveCohort({ cohortName });
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
