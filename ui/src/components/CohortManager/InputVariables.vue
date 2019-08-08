<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <input-variables-toolbar />
      <v-container fluid fill-height class="pa-0 pb-1">
        <input-variables-charts v-if="hasUserAddedInputVariables" />
        <v-layout v-else column align-center justify-center fill-height>
          <v-subheader class="display-1 primary--text text--lighten-5">
            ADD INPUT VARIABLES
          </v-subheader>
        </v-layout>
      </v-container>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapMutations, mapState } from 'vuex';
import { mutations, state } from '@/store/modules/cohortManager/types';
import InputVariablesToolbar from '@/components/CohortManager/InputVariablesToolbar.vue';
import InputVariablesCharts from '@/components/CohortManager/InputVariablesCharts.vue';

export default {
  components: {
    InputVariablesToolbar,
    InputVariablesCharts,
  },
  data() {
    return {
      variables: [],
      value: [],
    };
  },
  computed: {
    ...mapState('cohortManager', {
      inputVariables: state.INPUT_VARIABLES,
    }),
    hasUserAddedInputVariables() {
      return this.inputVariables.length > 0;
    },
  },
  methods: {
    ...mapMutations('cohortManager', {
      addInputVariable: mutations.ADD_INPUT_VARIABLE,
      removeInputVariable: mutations.REMOVE_INPUT_VARIABLE,
    }),
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
</style>
