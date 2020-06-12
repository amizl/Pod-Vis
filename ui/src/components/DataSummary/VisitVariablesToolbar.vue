<template>
  <section>
    <v-toolbar
      card
      dense
      flat
      color="white rounded-lg"
      class="toolbar_step_highlight"
    >
      <v-toolbar-title class="primary--text title">
        CHOOSE FIRST & LAST VISIT
      </v-toolbar-title>

      <v-divider vertical class="ml-4"> </v-divider>

      <v-chip color="primary" class="white--text title"
        >{{ collectionVarNames.length }} outcome variable<span
          v-if="collectionVarNames.length != 1"
          >s</span
        >&nbsp;selected</v-chip
      >
      <v-spacer />
      <v-toolbar-items>
        <v-chip
          :disabled="true"
          class="primary--text title"
          :style="'background: ' + colors['population']"
          >Study Population - {{ numSelectedSubjects }}</v-chip
        >
      </v-toolbar-items>
    </v-toolbar>

    <v-flex>
      <v-container fluid fill-height class="ma-0 pa-2">
        <v-select
          v-model="visitVariable"
          :items="visitItems"
          label="Select visit variable"
        >
        </v-select>

        <v-select
          v-model="firstVisit"
          :items="firstVisitEvents"
          label="Select first visit"
          :background-color="colors['firstVisit']"
          class="ml-2"
        >
        </v-select>

        <v-select
          v-model="lastVisit"
          :items="lastVisitEvents"
          label="Select last visit"
          :background-color="colors['lastVisit']"
          class="ml-2"
        >
        </v-select>

        <v-checkbox
          v-model="hideUnselectedVars"
          label="Hide unselected variables"
          class="ml-2"
        ></v-checkbox>
      </v-container>
    </v-flex>
  </section>
</template>

<script>
import axios from 'axios';
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dataSummary/types';
import { colors } from '@/utils/colors';
import { getObservationVariableNames } from '@/utils/helpers';

export default {
  data() {
    return {
      visitItems: ['Visit Event', 'Visit Number'],
      uniqueEvents: [],
      firstVisitEvents: [],
      lastVisitEvents: [],
      numSubjects: 0,
      colors: colors,
      hideUnselectedVars: true,
    };
  },
  computed: {
    ...mapState('dataSummary', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      collection: state.COLLECTION,
      collectionSummaries: state.COLLECTION_SUMMARIES,
      selFirstVisit: state.FIRST_VISIT,
      selLastVisit: state.LAST_VISIT,
      selVisitVariable: state.VISIT_VARIABLE,
      timesBetweenVisits: state.TIMES_BETWEEN_VISITS,
      numSelectedSubjects: state.NUM_SELECTED_SUBJECTS,
    }),
    collectionVarNames() {
      return Object.keys(getObservationVariableNames(this.collection));
    },
    visitVariable: {
      get() {
        return this.selVisitVariable;
      },
      set(value) {
        this.setVisitVariable(value);
        this.updateEvents();
        this.updateTimesBetweenVisits();
      },
    },
    lastVisit: {
      get() {
        return this.selLastVisit;
      },
      set(value) {
        this.setLastVisit(value);
        this.updateEvents();
        this.updateTimesBetweenVisits();
      },
    },
    firstVisit: {
      get() {
        return this.selFirstVisit;
      },
      set(value) {
        this.setFirstVisit(value);
        this.updateEvents();
        this.updateTimesBetweenVisits();
      },
    },
  },
  watch: {
    selFirstVisit(newval) {
      this.updateEvents();
      this.updateTimesBetweenVisits();
    },
    selLastVisit(newval) {
      this.updateEvents();
      this.updateTimesBetweenVisits();
    },
    hideUnselectedVars(newval) {
      this.$emit('hideUnselectedVars', newval);
    },
    collectionSummaries(newval) {
      this.updateTimesBetweenVisits();
    },
  },
  mounted() {
    this.updateEvents();
    this.updateTimesBetweenVisits();
  },
  methods: {
    updateEvents() {
      if (!this.collectionSummaries) {
        return;
      }
      // Identify the unique events
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );

      if (!this.selFirstVisit) {
        this.firstVisit = this.uniqueEvents[0];
      }
      if (!this.selLastVisit) {
        this.lastVisit = this.uniqueEvents[this.uniqueEvents.length - 1];
      }

      // possible first visit events - all those up until lastVisit
      this.firstVisitEvents = [];
      for (var i = 0; i < this.uniqueEvents.length; i++) {
        if (this.lastVisit && this.uniqueEvents[i] == this.lastVisit) {
          break;
        }
        this.firstVisitEvents.push(this.uniqueEvents[i]);
      }

      // possible last visit events - starting after firstVisit
      var firstVisitSeen = !this.firstVisit;
      this.lastVisitEvents = [];
      for (var i = 0; i < this.uniqueEvents.length; i++) {
        if (firstVisitSeen) {
          this.lastVisitEvents.push(this.uniqueEvents[i]);
        } else if (this.firstVisit && this.uniqueEvents[i] == this.firstVisit) {
          firstVisitSeen = true;
        }
      }
    },
    getColumn(anArray, columnNumber) {
      return anArray.map(function(row) {
        return row[columnNumber];
      });
    },
    getUniqueList(anArray) {
      var unique = anArray.filter((v, i, a) => a.indexOf(v) === i);
      return unique;
    },
    updateTimesBetweenVisits() {
      this.fetchTimesBetweenVisits();
    },
    ...mapActions('dataSummary', {
      setFirstVisit: actions.SET_FIRST_VISIT,
      setLastVisit: actions.SET_LAST_VISIT,
      setVisitVariable: actions.SET_VISIT_VARIABLE,
      fetchTimesBetweenVisits: actions.FETCH_TIMES_BETWEEN_VISITS,
    }),
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
