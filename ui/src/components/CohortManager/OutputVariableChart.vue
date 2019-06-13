<template>
  <v-sheet color="white" height="100%" min-width="200px">
    <v-layout column fill-height>
      <v-card-title class="subheading primary--text text--darken-4">
        {{ variable.parentLabel }} - {{ variable.label }}
        <v-spacer />
        <v-btn
          flat
          class="subheading primary--text text--lighten-4"
          @click="clearFilter({ dimension })"
        >
          Reset
        </v-btn>
      </v-card-title>
      <v-layout column fill-height>
        <v-flex>
          <span class="primary--text text--darken-4 ml-3">Population</span>
          <PopulationHistogramChart
            :id="variable.id"
            :dimension-name="dimension"
          />
        </v-flex>
        <v-flex>
          <span class="primary--text text--darken-4 ml-3">Selected Cohort</span>
          <HistogramChart :id="variable.id" :dimension-name="dimension" />
        </v-flex>
      </v-layout>
    </v-layout>
  </v-sheet>
</template>

<script>
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';
import PopulationHistogramChart from '@/components/CohortManager/HistogramChart/PopulationHistogramChart.vue';
import { mapActions } from 'vuex';
import { actions } from '@/store/modules/cohortManager/types';

export default {
  components: {
    HistogramChart,
    PopulationHistogramChart,
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
  created() {
    const [measure, id] = this.variable.id.split('-');

    const dimensionName = `${this.variable.parentLabel} - ${
      this.variable.label
    }`;

    this.dimension = dimensionName;
    const dimensionId = this.variable.parentID;

    const payload = {
      dimensionName: dimensionName,
      accessor: d => {
        let dimName = dimensionId;
        return d[dimName][measure];
      },
    };
    this.addDimension(payload);
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
      clearFilter: actions.CLEAR_FILTER,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
