<template>
  <div :key="chartsKey" class="xscrollable">
    <v-card class="d-flex flex-row">
      <v-card
	v-for="(outputVariable, index) in outputVariables"
	:key="outputVariable.id" :class="index > 0 ? 'ml-2' : ''">
        <output-variable-chart :variable="outputVariable" />
      </v-card>
    </v-card>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';
import OutputVariableChart from '@/components/CohortManager/OutputVariableChart.vue';
import resize from 'vue-resize-directive';

export default {
  directives: {
    resize,
  },
  components: {
    OutputVariableChart,
  },
  data() {
    return {
      chartsKey: 0,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      outputVariables: state.OUTPUT_VARIABLES,
    }),
  },
  watch: {
    /**
     * Watch for user adding input variables. When this happens,
     * we want to trigger a rerender so all the charts' dimensions
     * resize according to the available space in the flex area.
     * We can achieve a forecful rerender by updating the key of
     * the parent component.
     */
    outputVariables() {
      this.rerenderCharts();
    },
  },
  methods: {
    rerenderCharts() {
      this.chartsKey += 1;
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}

.xscrollable {
  overflow-x: auto;
  overflow-y: hidden;
}
</style>
