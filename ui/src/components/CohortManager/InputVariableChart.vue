<template>
  <v-sheet color="white" height="100%" min-width="300px">
    <v-layout column fill-height>
      <v-card-title class="subheading primary--text text--darken-4">
        <span style="margin: 0em;">
          <v-layout
            align-center
            style="background-color: white; padding: 0.4em 1.5em 0em 0.4em; border-radius: 0.5rem;"
          >
            <span style="padding:0em 0.5em 0em 0em">
              <img
                v-if="variable.label !== 'Dataset'"
                :src="'/images/' + variable.category + '-icon-128.png'"
                :title="variable.category"
                style="height:3em"
            /></span>
            <span class="subtitle-1">
              {{
                variable.type == 'observation' && variable.is_longitudinal
                  ? `${variable.parentLabel} - ${variable.label}`
                  : variable.label
              }}
            </span>
          </v-layout>
        </span>

        <v-spacer />
        <v-btn
          flat
          class="subheading primary--text text--lighten-4"
          @click="clearFilter({ dimension })"
        >
          Reset
        </v-btn>
      </v-card-title>
      <v-layout fill-height>
        <div v-if="variable.value_type === 'date'" class="pl-3">
          Date types not supported.
        </div>
        <ColumnChart
          v-else-if="
            (!variable.is_longitudinal &&
              variable.data_category === 'Categorical') ||
              variable.type === 'study'
          "
          :id="variable.id"
          :dimension-name="dimension"
          bar-tooltip="Click to add or remove this value from the cohort filter"
        />
        <HistogramChart
          v-else
          :id="variable.id"
          :dimension-name="dimension"
          :variable="variable"
          input-variable
        />
      </v-layout>
    </v-layout>
  </v-sheet>
</template>

<script>
import ColumnChart from '@/components/CohortManager/BarChart/BarChart.vue';
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';

export default {
  components: {
    ColumnChart,
    HistogramChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return { dimension: null };
  },
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      unfilteredData: state.UNFILTERED_DATA,
    }),
  },
  created() {
    this.addDimensionHelper(this.variable);
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
      clearFilter: actions.CLEAR_FILTER,
    }),
    addDimensionHelper(variable) {
      var dimensionName = null;
      var payload = null;

      // observation variable
      if (this.variable.type === 'observation') {
        var dimensionId = null;
        var measure = null;

        if (variable.is_longitudinal) {
          measure = this.variable.id.split('-')[0];
          dimensionName = `${this.variable.parentLabel} - ${
            this.variable.label
          }`;
          dimensionId = this.variable.parentID;
        } else {
          measure = 'value';
          dimensionName = variable.label;
          dimensionId = variable.id;
        }
        payload = {
          dimensionName,
          accessor: d => {
            const dimName = dimensionId;
            return d[dimName][measure];
          },
        };
      }
      // subject variable
      else {
        if (
          this.variable.label === 'Study' ||
          this.variable.label === 'Dataset'
        ) {
          dimensionName = this.variable.label;
          payload = {
            dimensionName: dimensionName,
            accessor: d => d.study.study_name,
          };
        } else {
          dimensionName = this.variable.label;
          payload = {
            dimensionName: dimensionName,
            accessor: d => {
              const dimName = dimensionName;
              return d[dimName];
            },
          };
        }
      }
      this.dimension = dimensionName;
      this.addDimension(payload);
    },
  },
};
</script>

<style lang="scss" scoped></style>
