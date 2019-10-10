<template>
  <section>
    <v-toolbar card dense flat color="white rounded-lg">
      <v-toolbar-items> <output-variables-dialog /> </v-toolbar-items>
      <v-divider vertical class="ml-4"></v-divider>
        <v-spacer />
      <v-toolbar-items>
      <!-- TODO...filters? -->
        <span class="subheading primary--text mt-3 mr-3">Show:</span>
        <v-btn-toggle mandatory v-model="subset" @change="doHighlightChange()">
         <v-btn text color="primary" class="white--text mr-2 py-1" value="cohort">Cohort</v-btn>
         <v-btn text color="#3FB551" class="white--text mr-2 py-1" value="non-cohort">Non-Cohort</v-btn>
        </v-btn-toggle>
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
  computed: {
    ...mapState('cohortManager', {
      highlighted_subset: state.HIGHLIGHTED_SUBSET,
    }),
  },
  data() {
    return {
      subset: 'cohort',
    };
  },
  methods: {
    ...mapActions('cohortManager', {
      setHighlightedSubset: actions.SET_HIGHLIGHTED_SUBSET,
    }),
    highlight(new_subset) {
      this.setHighlightedSubset(new_subset);
    },
    doHighlightChange() {
    if (typeof this.subset === 'undefined') {
        this.subset = 'cohort';
      }
      this.highlight(this.subset);
    },
  }
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
