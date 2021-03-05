<template>
  <v-container fluid fill-width class="ma-0 pa-0">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <v-card color="#eeeeee">
          <v-card-title class="primary--text pl-3 py-2">
            <output-variables-dialog
              :show-all-vars-checkbox="true"
              @dialogOpened="opened"
              @userSelectedOutputVariables="userSelectedOutputVariables"
            />

            <v-divider vertical class="ml-4 mr-4"> </v-divider>

            <v-tooltip bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span v-on="{ ...tooltip }">
                  <v-chip
                    label
                    color="primary"
                    class="white--text title mr-2"
                    >{{ outputVariables.length }}</v-chip
                  >
                  <span class="black--text text-body-1"
                    >Variable{{ outputVariables.length == 1 ? '' : 's' }}</span
                  >
                </span>
              </template>
              <span class="subtitle-1">
                {{ outputVariables.length }} output variable{{
                  outputVariables.length == 1 ? '' : 's'
                }}
                selected
              </span>
            </v-tooltip>

            <v-spacer />

            <v-toolbar-items v-if="false">
              <span class="subheading primary--text mt-3 mr-3">Show:</span>
              <v-btn-toggle
                v-model="subset"
                mandatory
                style="background: rgb(255,255,255,0)"
                @change="doHighlightChange()"
              >
                <v-btn
                  text
                  :color="colors['cohort']"
                  class="white--text mr-2 py-1"
                  value="cohort"
                  >Cohort</v-btn
                >
                <v-btn
                  text
                  :color="colors['nonCohort']"
                  class="white--text mr-2 py-1"
                  value="non-cohort"
                  >Non-Cohort</v-btn
                >
              </v-btn-toggle>
            </v-toolbar-items>

            <!--
      <v-toolbar-items>
        <v-icon v-if="expanded" @click="expandClicked">expand_less</v-icon>
        <v-icon v-else @click="expandClicked">expand_more</v-icon>
      </v-toolbar-items>
      -->
            <v-chip
              v-if="showHelpChip"
              label
              close
              color="#4caf50"
              class="font-weight-bold white--text pa-3 my-5"
              @click:close="showHelpChip = false"
              >Review the outcome graphs and analytics panel.</v-chip
            >
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import OutputVariablesDialog from '@/components/CohortManager/OutputVariablesDialog.vue';
import { colors } from '@/utils/colors';

export default {
  components: {
    OutputVariablesDialog,
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
    showReviewHelp: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      subset: 'cohort',
      colors: colors,
      showHelpChip: false,
    };
  },
  watch: {
    showReviewHelp(show) {
      this.showHelpChip = show;
    },
  },
  computed: {
    ...mapState('cohortManager', {
      highlighted_subset: state.HIGHLIGHTED_SUBSET,
      outputVariables: state.OUTPUT_VARIABLES,
    }),
  },
  methods: {
    ...mapActions('cohortManager', {
      setHighlightedSubset: actions.SET_HIGHLIGHTED_SUBSET,
    }),
    expandClicked() {
      this.$emit('expandClicked', !this.expanded);
    },
    userSelectedOutputVariables() {
      this.$emit('userSelectedOutputVariables', true);
    },
    highlight(newSubset) {
      this.setHighlightedSubset(newSubset);
    },
    doHighlightChange() {
      if (typeof this.subset === 'undefined') {
        this.subset = 'cohort';
      }
      this.highlight(this.subset);
    },
    getToolbarClass() {
      if (this.highlighted) {
        return 'toolbar_step_highlight';
      } else {
        return '';
      }
    },
    opened() {
      this.$emit('expandClicked', true);
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
.scrollable {
  overflow-x: auto;
}
.scrollable::-webkit-scrollbar {
  display: none;
}
</style>
