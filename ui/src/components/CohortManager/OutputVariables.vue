<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <output-variables-toolbar />
      <v-container fluid fill-height>
        <!-- <input-variables-charts v-if="hasUserAddedOutputVariables" /> -->
        <v-layout column align-center justify-center fill-height>
          <v-subheader class="display-1 primary--text text--lighten-5">
            ADD OUTPUT VARIABLES
          </v-subheader>
        </v-layout>
      </v-container>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapMutations, mapState } from 'vuex';
import { mutations, state } from '@/store/modules/cohortManager/types';
import OutputVariablesToolbar from '@/components/CohortManager/OutputVariablesToolbar.vue';

export default {
  components: {
    OutputVariablesToolbar,
  },
  data() {
    return {
      variables: [],
      value: [],
    };
  },
  computed: {
    // ...mapState('cohortManager', {
    // outputVariables: state.OUTPUT_VARIABLES,
    // }),
    hasUserAddedOutVariables() {
      return false;
      // return this.outputVariables.length > 0;
    },
  },
  methods: {
    // ...mapMutations("cohortManager", {
    //   addInputVariable: mutations.ADD_INPUT_VARIABLE,
    //   removeInputVariable: mutations.REMOVE_INPUT_VARIABLE
    // })
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
</style>
