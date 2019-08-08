<template>
  <v-sheet color="white" height="100%" min-width="350px" max-width="350px">
    <v-layout column fill-height>
      <v-card-title class="subheading primary--text text--darken-4 pb-0">
        <span v-if="variable.parentLabel">
          {{ variable.parentLabel }} - {{ variable.label }}
        </span>
        <span v-else> {{ variable.label }} </span>
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
import { mapActions } from 'vuex';
import { actions } from '@/store/modules/cohortManager/types';

export default {
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
  },
};
</script>

<style lang="scss" scoped></style>
