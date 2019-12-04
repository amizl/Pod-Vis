<template>
  <v-layout :key="chartsKey" :class="classes">
    <v-flex v-for="outputVariable in outputVariables" :key="outputVariable.id">
      <v-layout fill-height>
        <v-flex fill-height>
          <output-variable-chart :variable="outputVariable" />
        </v-flex>
        <!-- <v-flex v-if="index < outputVariables.length - 1" shrink>
          <v-divider vertical></v-divider>
        </v-flex> -->
      </v-layout>
    </v-flex>
    <v-flex fill-width></v-flex>
  </v-layout>
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
    classes() {
      return {
        // When the user has specified more variables
        // then what the container can fit, make
        scrollable: true, // this.outputVariables > 5,
      };
    },
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

.scrollable {
  overflow-x: auto;
}
.scrollable::-webkit-scrollbar {
  display: none;
}
</style>
