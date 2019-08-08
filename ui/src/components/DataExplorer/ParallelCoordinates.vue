<template>
  <v-sheet
    color="white"
    height="100%"
    min-width="200px"
    :class="classed"
    @click="toggled = !toggled"
  >
    <v-layout column fill-height>
      <v-card-title class="subheading primary--text text--darken-4">
        {{
          variable.type == 'observation'
            ? `${variable.parentLabel} - ${variable.label}`
            : variable.label
        }}
        <v-spacer />
      </v-card-title>
      <parallel-coordinates-chart
        :variable="variable"
        :dimension-name="variable.id"
      />
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';
import ParallelCoordinatesChart from '@/components/DataExplorer/ParallelCoordinatesChart.vue';

export default {
  components: {
    ParallelCoordinatesChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      toggled: false,
    };
  },
  computed: {
    classed() {
      return {
        'elevation-4': this.toggled,
        'pa-1': this.toggled,
        'zoom-in': !this.toggled,
        'zoom-out': this.toggled,
      };
    },
  },
  created() {},
  methods: {},
};
</script>

<style scoped>
.zoom-in {
  cursor: zoom-in;
}
.zoom-out {
  cursor: zoom-out;
}
</style>
