<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow pa-0 ma-0">
    <output-variables-toolbar
      :expanded="expanded"
      :highlighted="highlighted"
      :show-review-help="showReviewHelp"
      class="ma-0 pa-0"
      @expandClicked="expandClicked"
      @userSelectedOutputVariables="userSelectedOutputVariables"
    />
    <v-container v-show="true" fluid fill-width class="pa-0 ma-0">
      <v-row class="pa-0 ma-0">
        <v-col cols="12">
          <v-chip
            v-if="showHelpChip"
            label
            close
            color="#4caf50"
            class="font-weight-bold white--text pa-3 my-5"
            @click:close="showHelpChip = false"
            >Click on
            <v-icon dark medium class="px-2 white--text" color="primary"
              >add_circle</v-icon
            >
            button and select one or more outcome variables.</v-chip
          >

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
    showAddHelp: {
      type: Boolean,
      required: false,
      default: false,
    },
    showReviewHelp: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      variables: [],
      value: [],
      showHelpChip: false,
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
  watch: {
    showAddHelp(show) {
      this.showHelpChip = show;
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
