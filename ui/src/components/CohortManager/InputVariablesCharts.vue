<template>
  <div :key="chartsKey" class="xscrollable px-2">
    <v-card class="d-flex flex-row pb-1">
      <v-card
        v-for="(inputVariable, index) in inputVariables"
        :key="inputVariable.id"
        :class="index > 0 ? 'ml-2 pb-1' : 'pb-1'"
      >
        <input-variable-chart
          :variable="inputVariable"
          @userResetInputVariable="userChangedVariable"
          @userChangedInputVariable="userChangedVariable"
        />
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
    userChangedVariable(v) {
      this.$emit('userChangedInputVariable', true);
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
.scrollable::-webkit-scrollbar {
  display: none;
}
</style>
