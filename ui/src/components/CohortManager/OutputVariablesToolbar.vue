<template>
  <section>
    <v-toolbar card dense flat :color="getToolbarColor()" class="rounded-lg">
      <v-toolbar-items>
        <output-variables-dialog @dialogOpened="opened" />
      </v-toolbar-items>
      <v-divider vertical class="ml-4"></v-divider>
      <v-chip
        v-if="outputVariables.length == 0"
        disabled
        color="primary"
        class="white--text title"
        >No variables selected</v-chip
      >
      <v-chip v-else disabled color="primary" class="white--text title"
        >{{ outputVariables.length }} variable<span
          v-if="outputVariables.length != 1"
          >s</span
        >&nbsp;selected</v-chip
      >
      <v-spacer />
      <v-toolbar-items>
        <!-- TODO...filters? -->
        <span class="subheading primary--text mt-3 mr-3">Show:</span>
        <v-btn-toggle v-model="subset" mandatory @change="doHighlightChange()">
          <v-btn
            text
            color="primary"
            class="white--text mr-2 py-1"
            value="cohort"
            >Cohort</v-btn
          >
          <v-btn
            text
            color="#3FB551"
            class="white--text mr-2 py-1"
            value="non-cohort"
            >Non-Cohort</v-btn
          >
        </v-btn-toggle>
      </v-toolbar-items>
      <v-toolbar-items>
        <v-icon v-if="expanded" @click="expandClicked">expand_less</v-icon>
        <v-icon v-else @click="expandClicked">expand_more</v-icon>
      </v-toolbar-items>
    </v-toolbar>
    <v-divider></v-divider>
  </section>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import OutputVariablesDialog from '@/components/CohortManager/OutputVariablesDialog.vue';

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
  },
  data() {
    return {
      subset: 'cohort',
    };
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
    highlight(newSubset) {
      this.setHighlightedSubset(newSubset);
    },
    doHighlightChange() {
      if (typeof this.subset === 'undefined') {
        this.subset = 'cohort';
      }
      this.highlight(this.subset);
    },
    getToolbarColor() {
      if (this.highlighted) {
        return 'rgb(212,197,71,0.2)';
      } else {
        return 'white';
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
