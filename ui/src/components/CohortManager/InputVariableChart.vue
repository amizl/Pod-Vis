<template>
  <v-sheet color="white" height="100%" min-width="300px">
    <v-layout column fill-height>
      <v-card-title class="subheading primary--text text--darken-4">
        {{
          variable.type == 'observation'
            ? `${variable.parentLabel} - ${variable.label}`
            : variable.label
        }}
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
        <ColumnChart
          v-if="
            (variable.type === 'subject' || variable.type === 'study') &&
              typeof unfilteredData[0][dimension] != 'number'
          "
          :id="variable.id"
          :dimension-name="dimension"
        />
        <HistogramChart v-else :id="variable.id" :dimension-name="dimension" />
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
    if (this.variable.type === 'observation') {
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
    } else {
      let dimension, payload;
      if (this.variable.type == 'study') {
        dimension = this.variable.label;
        payload = {
          dimensionName: dimension, // GET STUDY NAME HERE...
          accessor: d => d.study.study_name,
        };
      } else {
        dimension = this.variable.label;
        payload = {
          dimensionName: dimension,
          accessor: d => {
            let dimName = dimension;
            return d[dimName];
          },
        };
      }
      this.dimension = dimension;
      this.addDimension(payload);
    }
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
