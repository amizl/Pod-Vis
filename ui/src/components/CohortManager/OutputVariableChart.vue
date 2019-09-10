<template>
  <v-sheet color="white" height="100%" min-width="350px" max-width="350px">
    <v-layout column fill-height v-bind:class="getOutcomeClass(variable)">
      <v-card-title v-bind:class="getTitleClass(variable)">
        <span style='margin: 0em 0em 1em 0em;'>
          <v-layout align-center style='background-color: white; padding: 0.4em 0.4em 0em 0.4em; border-radius: 0.5rem;'>
	    <span style="padding:0em 0.5em 0em 0em">
                <img
                  :src="'/images/' + variable.parent.label + '-icon-64.png'"
                  style="height:2em"
              /></span>
              {{ getVariableLabel(variable) }}
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
        v-if="variable.children"
        :key="resetCount"
        :variable="variable"
        :dimension-name="dimension"
      />
      <HistogramChart
        v-else
        :id="variable.id"
        :key="resetCount"
        :dimension-name="dimension"
      />
    </v-layout>
  </v-sheet>
</template>

<script>
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';
import MultiChart from '@/components/CohortManager/MultiChart.vue';
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  computed: {
    ...mapState('cohortManager', {
      pvals: state.PVALS,
      pval_threshold: state.PVAL_THRESHOLD,
    }),
  },
  components: {
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
      const [measure, id] = variable.id.split('-');
      const dimensionName = `${variable.parentLabel} - ${variable.label}`;

      this.dimension = dimensionName;
      const dimensionId = variable.parentID;

      const payload = {
        dimensionName: dimensionName,
        accessor: d => {
          let dimName = dimensionId;
          return d[dimName][measure];
        },
      };
      this.addDimension(payload);
    },
    isBelowPValThreshold(v) {
      for (var pv in this.pvals) {
        if (this.pvals[pv].label === v.label) {
          if (this.pvals[pv].pval <= this.pval_threshold) {
	    return true;
	  }
	}
      }
      return false;
    },
    getTitleClass(v) {
      var dflt = 'subheading primary--text text--darken-4 pb-0';
      if (this.isBelowPValThreshold(v)) {
        return dflt + ' highlight-var';
      } else {
        return dflt;
      }
    },
    getOutcomeClass(v) {
      if (this.isBelowPValThreshold(v)) {
        return 'highlight-var-chart';
     } else {
        return 'var-chart';
      }
    },
    getVariableLabel(v) {
      if (v.parentLabel) {
     	return v.parentLabel + " - " + v.label;
      } else {
      	return v.label;
      }
    }
},
};
</script>

<style lang="scss" scoped></style>
