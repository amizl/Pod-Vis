<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <output-variables-toolbar
        :expanded="expanded"
        :highlighted="highlighted"
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
  props: {
    expanded: {
      type: Boolean,
      required: true,
    },
    highlighted: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      variables: [],
      value: [],
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
    expandClicked(newval) {
      this.$emit('update:expanded', newval);
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
</style>
