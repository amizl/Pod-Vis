<template>
  <v-sheet color="white" height="100%" min-width="200px">
    <v-layout column fill-height>
      <v-card-title class="title primary--text text--darken-4">
        {{ dimension }}
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
          v-if="variable.type === 'subject'"
          :id="variable.id"
          :dimension-name="dimension"
        />
        <div v-else></div>
      </v-layout>
    </v-layout>
  </v-sheet>
</template>

<script>
import ColumnChart from '@/components/CohortManager/BarChart/BarChart.vue';
import { mapActions } from 'vuex';
import { actions } from '@/store/modules/cohortManager/types';

export default {
  components: {
    ColumnChart,
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
    this.dimension = this.variable.label;
    this.addDimension(this.dimension);
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
