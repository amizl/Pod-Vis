<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <output-variables-toolbar
        :expanded="expanded"
        @expandClicked="expandClicked"
      />
      <v-container v-show="expanded" fluid fill-height class="pa-0 pb-1">
        <output-variables-charts v-if="hasUserAddedOutputVariables" />
        <v-layout v-else column align-center justify-center fill-height>
          <v-subheader class="display-1 primary--text text--lighten-5">
            ADD OUTCOME VARIABLES
          </v-subheader>
        </v-layout>
      </v-container>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';
import OutputVariablesToolbar from '@/components/CohortManager/OutputVariablesToolbar.vue';
import OutputVariablesCharts from '@/components/CohortManager/OutputVariablesCharts.vue';

export default {
  components: {
    OutputVariablesToolbar,
    OutputVariablesCharts,
  },
  data() {
    return {
      variables: [],
      value: [],
      expanded: true,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      outputVariables: state.OUTPUT_VARIABLES,
    }),
    hasUserAddedOutputVariables() {
      return this.outputVariables.length > 0;
    },
  },
  methods: {
    // ...mapMutations("cohortManager", {
    //   addInputVariable: mutations.ADD_INPUT_VARIABLE,
    //   removeInputVariable: mutations.REMOVE_INPUT_VARIABLE
    // })
    expandClicked(newval) {
      this.expanded = newval;
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
</style>
