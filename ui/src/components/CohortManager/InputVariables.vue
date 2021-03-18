<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow pa-0 ma-0">
    <input-variables-toolbar
      :expanded="expanded"
      :highlighted="highlighted"
      class="ma-0 pa-0"
      @expandClicked="expandClicked"
      @userSelectedInputVariables="userSelectedInputVariables"
    />
    <v-container v-show="expanded" fluid fill-width class="pa-0 ma-0">
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
            button and select one or more predictor variables.</v-chip
          >

          <input-variables-charts
            v-if="hasUserAddedInputVariables"
            :show-filter-help="showFilterHelp"
            :show-analytics-help="showAnalyticsHelp"
            @userChangedInputVariable="userChangedInputVariable"
            @comparePredefinedRanges="comparePredefinedRanges"
            @savePredefinedRanges="savePredefinedRanges"
          />
          <v-subheader
            v-else
            class="subheading primary--text text--lighten-4 text-h6"
          >
            CHOOSE PREDICTOR VARIABLES
          </v-subheader>
        </v-col>
      </v-row>
    </v-container>
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
    showFilterHelp: {
      type: Boolean,
      required: false,
      default: false,
    },
    showAnalyticsHelp: {
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
  watch: {
    showAddHelp(show) {
      this.showHelpChip = show;
    },
  },
  computed: {
    ...mapState('cohortManager', {
      inputVariables: state.INPUT_VARIABLES,
      helpMode: state.HELP_MODE,
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
    expandClicked(newval) {
      this.$emit('update:expanded', newval);
    },
    userSelectedInputVariables() {
      this.$emit('userSelectedInputVariables', true);
    },
    userChangedInputVariable() {
      this.$emit('userChangedInputVariable', true);
    },
    comparePredefinedRanges(ranges) {
      this.$emit('comparePredefinedRanges', ranges);
    },
    savePredefinedRanges(ranges) {
      this.$emit('savePredefinedRanges', ranges);
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
</style>
