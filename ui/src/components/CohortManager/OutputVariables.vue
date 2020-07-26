<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow pa-0 ma-0">
    <output-variables-toolbar
      :expanded="expanded"
      :highlighted="highlighted"
      @expandClicked="expandClicked"
      class="ma-0 pa-0"
      />
    <v-container v-show="expanded" fluid fill-width class="pa-0 pb-1 ma-0">
      <v-row>
	<v-col cols="12">
          <output-variables-charts v-if="hasUserAddedOutputVariables" />
          <div v-else class="display-1 primary--text text--lighten-5 mb-5 pa-5" align="center" justify="center">
            ADD OUTCOME VARIABLES
          </div>
	</v-col>
      </v-row>
    </v-container>
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
