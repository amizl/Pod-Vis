<template>
  <v-sheet class="ma-1" color="white" height="100%" width="400px">
    <v-layout column fill-height class="var-chart">
      <v-card-title :class="getTitleClass(variable)">
        <span style="margin: 0em;">
          <v-layout
            align-center
            style="background-color: white; padding: 0.4em 1.5em 0em 0.4em; border-radius: 0.5rem;"
          >
            <span style="padding:0em 0.5em 0em 0em">
              <img
                :src="'/images/' + variable.category + '-icon-128.png'"
                :title="variable.category"
                style="height:3em"
            /></span>
            <span class="subtitle-1">{{ getVariableLabel(variable) }}</span>
          </v-layout>
        </span>
        <!-- <v-btn
          flat
          class="subheading primary--text text--lighten-4"
          @click="clearFilter({ dimension })"
        >
          Reset
        </v-btn> -->
      </v-card-title>
      <MultiChart
        :key="resetCount"
        class="ma-1"
        :variable="variable"
        :dimension-name="dimension"
        :highlight-change="isBelowPValThreshold(variable)"
      />
    </v-layout>
  </v-sheet>
</template>

<script>
import MultiChart from '@/components/CohortManager/MultiChart.vue';
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  components: {
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
    addDimensionHelper(variable) {
      const measure = variable.id.split('-')[0];
      const dimensionName = `${variable.parentLabel} - ${variable.label}`;

      this.dimension = dimensionName;
      const dimensionId = variable.parentID;

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
      const dflt = 'subheading primary--text text--darken-4 pb-0';
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
