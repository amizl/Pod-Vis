<template>
  <v-sheet class="ma-1" color="white" height="100%" min-width="400px">
    <v-layout column fill-height class="var-chart">
      <v-card-title :class="getTitleClass(variable)">
        <v-layout
          align-center
          style="background-color: white; padding: 0.5em 0em 1em 0.4em; border-radius: 0.5rem;"
        >
          <span style="padding:0.4em 0.5em 1em 0.5em">
            <img
              :src="'/images/' + variable.category + '-icon-128.png'"
              :title="variable.category"
              style="height: 3em; padding: 0em 0.5em 0em 0em;"
            />
          </span>
          <span class="subtitle-1">{{ getVariableLabel(variable) }}</span>
          <v-spacer />
          <v-btn
            text
            flat
            small
            no-padding
            class="together subheading primary--text text--lighten-4"
            @click="clearAllFilters({ dimension })"
          >
            Reset
          </v-btn>
        </v-layout>
      </v-card-title>

      <v-layout fill-height>
        <div v-if="variable.value_type === 'date'" class="pl-3">
          Date types not supported.
        </div>
        <ColumnChart
          v-else-if="
            variable.is_longitudinal === false &&
              variable.data_category === 'Categorical'
          "
          :id="variable.id"
          :dimension-name="dimension"
        />
        <HistogramChart
          v-else-if="variable.is_longitudinal === false"
          :id="variable.id"
          :dimension-name="variable.label"
          :input-variable="false"
          :variable="variable"
        />
        <MultiChart
          v-else
          :key="resetCount"
          class="ma-1"
          :variable="variable"
          :dimension-name="dimension"
          :highlight-change="isBelowPValThreshold(variable)"
          width="400px"
        />
        <v-flex fill-width> </v-flex>
      </v-layout>
    </v-layout>
  </v-sheet>
</template>

<script>
import ColumnChart from '@/components/CohortManager/BarChart/BarChart.vue';
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';
import MultiChart from '@/components/CohortManager/MultiChart.vue';
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  components: {
    ColumnChart,
    HistogramChart,
    MultiChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return { dimension: null, resetCount: 0 };
  },
  computed: {
    ...mapState('cohortManager', {
      pvals: state.PVALS,
      pval_threshold: state.PVAL_THRESHOLD,
      dimensions: state.DIMENSIONS,
    }),
  },
  created() {
    if (this.variable.children) {
      this.variable.children.forEach(childVariable => {
        this.addDimensionHelper(childVariable);
      });
      this.dimension = this.variable.id;
    } else {
      this.addDimensionHelper(this.variable);
    }
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
      clearFilter: actions.CLEAR_FILTER,
    }),
    clearAllFilters(dim) {
      this.clearFilter(dim);
      // cover all the bases for the MultiChart/longitudinal case
      this.clearFilter({ dimension: this.variable.label + ' - First Visit' });
      this.clearFilter({ dimension: this.variable.label + ' - Last Visit' });
      this.clearFilter({ dimension: this.variable.label + ' - Change' });
      this.clearFilter({
        dimension: this.variable.label + ' - Rate of Change',
      });
    },
    addDimensionHelper(variable) {
      var measure = null;
      var dimensionName = null;
      var dimensionId = null;

      if (variable.is_longitudinal) {
        measure = variable.id.split('-')[0];
        dimensionName = `${variable.parentLabel} - ${variable.label}`;
        this.dimension = dimensionName;
        dimensionId = variable.parentID;
      } else {
        measure = 'value';
        dimensionName = variable.label;
        this.dimension = dimensionName;
        dimensionId = variable.id;
      }
      const payload = {
        dimensionName,
        accessor: d => {
          const dimName = dimensionId;
          return d[dimName][measure];
        },
      };
      this.addDimension(payload);
    },
    isBelowPValThreshold(v) {
      const pvt = this.pval_threshold;
      let rv = false;
      if (!this.pvals) {
        return false;
      }
      this.pvals.forEach(pv => {
        if (
          pv.label === v.label ||
          (pv.label === v.parentLabel && v.label === 'Change')
        ) {
          if (pv.pval < pvt) {
            rv = true;
          }
        }
      });
      return rv;
    },
    getTitleClass(v) {
      const dflt =
        'subheading primary--text text--darken-4 pa-1 ma-0 text-truncate';
      if (this.isBelowPValThreshold(v)) {
        return `${dflt} highlight-var`;
      }
      return `${dflt} not-highlight-var`;
    },
    getOutcomeClass(v) {
      if (this.isBelowPValThreshold(v)) {
        return 'highlight-var-chart';
      }
      return 'var-chart';
    },
    getVariableLabel(v) {
      if (v.parentLabel) {
        return `${v.parentLabel} - ${v.label}`;
      }
      return v.label;
    },
  },
};
</script>

<style lang="scss" scoped></style>
