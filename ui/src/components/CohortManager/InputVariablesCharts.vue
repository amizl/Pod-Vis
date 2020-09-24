<template>
  <div class="xscrollable px-2">
    <v-card class="d-flex flex-row pb-1">
      <v-card
        v-for="(inputVariable, index) in inputVariables"
        :key="'ivcc-' + inputVariable.id"
        :class="index > 0 ? 'ml-2 pb-1' : 'pb-1'"
      >
        <input-variable-chart
          :key="'ivc-' + inputVariable.id"
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
  computed: {
    ...mapState('cohortManager', {
      inputVariables: state.INPUT_VARIABLES,
    }),
  },
  methods: {
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
