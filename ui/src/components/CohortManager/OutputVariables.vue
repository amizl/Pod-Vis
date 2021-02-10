<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow pa-0 ma-0">
    <output-variables-toolbar
      :expanded="expanded"
      :highlighted="highlighted"
      class="ma-0 pa-0"
      @expandClicked="expandClicked"
      @userSelectedOutputVariables="userSelectedOutputVariables"
    />
    <v-container v-show="true" fluid fill-width class="pa-0 ma-0">
      <v-row class="pa-0 ma-0">
        <v-col cols="12">
          <output-variables-charts
            v-if="hasUserAddedOutputVariables"
            @userChangedOutputVariable="userChangedOutputVariable"
          />
          <v-subheader
            v-else
            class="subheading primary--text text--lighten-4 text-h6"
          >
            CHOOSE OUTCOME VARIABLES
          </v-subheader>
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
    userSelectedOutputVariables() {
      this.$emit('userSelectedOutputVariables', true);
    },
    userChangedOutputVariable() {
      this.$emit('userChangedOutputVariable', true);
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
</style>
