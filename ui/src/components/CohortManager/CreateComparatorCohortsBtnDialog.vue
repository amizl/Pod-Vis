<template>
  <div>
    <v-btn color="primary--text" @click="dialog = !dialog">
      <v-icon left>save</v-icon> CREATE COMPARATOR COHORTS
    </v-btn>
    <v-dialog v-model="dialog" width="500" persistent>
      <v-card class="rounded-lg">
        <v-card-title primary-title>
          <span class="primary--text title pl-2"
            >Create Comparator Cohorts</span
          >
          <br clear="both" />
          <span class="primary--text subtitle pl-2"
            >based on {{ dimensionName }}:</span
          >
          <span
            v-if="!outputVariables || outputVariables.length == 0"
            class="red--text title pl-2 pt-4"
          >
            WARNING:<br clear="both" /><br clear="both" />No outcome variables
            selected.
          </span>
          <span
            v-else-if="hasUserFilteredOutputVariables"
            class="red--text title pl-2 pt-4"
          >
            WARNING:<br clear="both" /><br clear="both" />Outcome variable
            filters will not be saved with the cohort unless they are moved to
            the PREDICTOR VARIABLES section.
          </span>
        </v-card-title>

        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="onSave">
            <v-select
              v-model="rangeType"
              :items="['current cohort', 'study population']"
              label="Create comparator cohorts based on"
            >
            </v-select>

            <v-select
              v-model="cohortChoice"
              :items="cohortChoices"
              label="Select comparator cohorts to create"
              item-text="label"
              return-object
            >
            </v-select>
            <v-text-field
              ref="vtf"
              v-model="cohortNamePrefix"
              :rules="[
                () => !!cohortNamePrefix || 'Cohort name prefix is required.',
                () =>
                  cohortNamePrefixOK() ||
                  'A cohort with that name prefix already exists.',
              ]"
              prepend-inner-icon="table_chart"
              label="Comparator cohort name prefix:"
              filled
              text
              background-color="grey lighten-4"
              class="mt-2"
            >
            </v-text-field>
            <span v-if="cohortChoice" class="primary--text body-1 mb-2">
              The following cohorts will be created:
              <ul>
                <li v-for="n in newCohorts()" :key="n.id">{{ n.name }}</li>
              </ul>
            </span>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="red lighten-2" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn
            :disabled="
              !cohortChoice || !cohortNamePrefix || !cohortNamePrefixOK()
            "
            :loading="loading"
            color="primary"
            @click="onSave"
          >
            <v-icon left>save</v-icon> Create {{ numCohorts() }} Cohorts</v-btn
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
    resetSelection: {
      type: Function,
      required: true,
    },
    selectCohortRange: {
      type: Function,
      required: true,
    },
    dimensionName: {
      type: String,
      required: true,
    },
  },
  data: () => ({
    cohortNamePrefix: '',
    rangeType: 'current cohort',
    valid: true,
    dialog: false,
    loading: false,
    cohortChoice: null,
    cohortChoices: [
      {
        label: '2 cohorts - top 1/2, bottom 1/2',
        cohorts: [
          { label: 'bottom 1/2', min: 'min', max: [1, 2] },
          { label: 'top 1/2', min: [1, 2], max: 'max' },
        ],
      },
      {
        label: '2 cohorts - bottom 1/4, top 3/4',
        cohorts: [
          { label: 'bottom 1/4', min: 'min', max: [1, 4] },
          { label: 'top 3/4', min: [1, 4], max: 'max' },
        ],
      },
      {
        label: '2 cohorts - bottom 3/4, top 1/4',
        cohorts: [
          { label: 'bottom 3/4', min: 'min', max: [3, 4] },
          { label: 'top 1/4', min: [3, 4], max: 'max' },
        ],
      },
      {
        label: '3 cohorts - top 1/3, middle 1/3, bottom 1/3',
        cohorts: [
          { label: 'bottom 1/3', min: 'min', max: [1, 3] },
          { label: 'middle 1/3', min: [1, 3], max: [2, 3] },
          { label: 'top 1/3', min: [2, 3], max: 'max' },
        ],
      },
      {
        label: '4 cohorts - 4 quartiles',
        cohorts: [
          { label: '1st quartile', min: 'min', max: [1, 4] },
          { label: '2nd quartile', min: [1, 4], max: [1, 2] },
          { label: '3rd quartile', min: [1, 2], max: [3, 4] },
          { label: '4th quartile', min: [3, 4], max: 'max' },
        ],
      },
    ],
  }),
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      cohort: state.COHORT,
      cohorts: state.COHORTS,
      outputVariables: state.OUTPUT_VARIABLES,
    }),
    ...mapGetters('cohortManager', {
      hasUserFilteredInputVariables: getters.HAS_USER_FILTERED_INPUT_VARIABLES,
      hasUserFilteredOutputVariables:
        getters.HAS_USER_FILTERED_OUTPUT_VARIABLES,
    }),
    // TODO - factor this out
    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;

      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          cch.push(e);
        }
      });

      return cch;
    },
    cohortNames() {
      return this.collection_cohorts.map(c => c.label);
    },
  },
  watch: {
    dialog(val) {
      if (val) {
        this.resetSelection();
        this.showing();
      }
    },
  },
  created() {
    this.cohortNamePrefix = this.dimensionName;
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
    numCohorts() {
      if (!this.cohortChoice) {
        return 0;
      }
      return this.cohortChoice.cohorts.length;
    },
    cohortNamePrefixOK() {
      var name_ok = true;
      this.cohortNames.forEach(cn => {
        if (cn.startsWith(this.cohortNamePrefix)) {
          name_ok = false;
        }
      });
      return name_ok;
    },
    newCohorts() {
      var cohorts = [];
      var nCohorts = this.cohortChoice.cohorts.length;
      var rangeSuffix = '[C]';
      if (this.rangeType.startsWith('study population')) {
        rangeSuffix = '[P]';
      }
      for (var c = 0; c < nCohorts; c++) {
        var cohort = this.cohortChoice.cohorts[c];
        var cohortName =
          this.cohortNamePrefix + ' - ' + cohort.label + ' ' + rangeSuffix;
        cohorts.push({ id: c + 1, name: cohortName, cohort: cohort });
      }
      return cohorts;
    },
    async onSave() {
      if (this.$refs.form.validate()) {
        this.loading = true;
        try {
          var cohorts = this.newCohorts();

          var nCohorts = cohorts.length;
          for (var c = 0; c < nCohorts; c++) {
            var cohort = cohorts[c];
            this.selectCohortRange(cohort.cohort, this.rangeType);
            await this.saveCohort({ cohortName: cohort.name });
          }

          this.loading = false;
          this.dialog = false;
          this.$emit('cohortsSaved', true);
        } catch (err) {
          this.loading = false;
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
