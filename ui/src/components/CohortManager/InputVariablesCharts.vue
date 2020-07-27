<template>
  <div :key="chartsKey" :class="classes">
    <v-card class="d-flex flex-row">
      <v-card
        v-for="(inputVariable, index) in inputVariables"
        :key="inputVariable.id"
        :class="index > 0 ? 'ml-2' : ''"
      >
        <input-variable-chart :variable="inputVariable" />
      </v-card>
    </v-card>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';
import InputVariableChart from '@/components/CohortManager/InputVariableChart.vue';
import resize from 'vue-resize-directive';

export default {
  directives: {
    resize,
  },
  components: {
    InputVariableChart,
  },
  data() {
    return {
      chartsKey: 0,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      inputVariables: state.INPUT_VARIABLES,
    }),
    classes() {
      return {
        // When the user has specified more variables
        // then what the container can fit, make
        scrollable: true, // this.inputVariables > 5,
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
    inputVariables() {
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
