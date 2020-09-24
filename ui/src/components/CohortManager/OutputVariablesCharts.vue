<template>
  <div class="xscrollable px-2">
    <v-card class="d-flex flex-row pb-1">
      <v-card
        v-for="(outputVariable, index) in outputVariables"
        :key="'vc-' + outputVariable.id"
        :class="index > 0 ? 'ml-2 pb-1' : 'pb-1'"
      >
        <output-variable-chart
          :key="'ovc-' + outputVariable.id"
          :variable="outputVariable"
          @userResetOutputVariable="userChangedVariable"
          @userChangedOutputVariable="userChangedVariable"
        />
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
  computed: {
    ...mapState('cohortManager', {
      outputVariables: state.OUTPUT_VARIABLES,
    }),
  },
  methods: {
    userChangedVariable() {
      this.$emit('userChangedOutputVariable', true);
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
