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
        >{{ collection.observation_variables.length }} variable<span
          v-if="collection.observation_variables.length != 1"
          >s</span
        >&nbsp;selected</v-chip
      >
      <v-spacer />
      <v-toolbar-items>
        <v-chip
          :disabled="true"
          class="primary--text title"
          :style="'background: ' + colors['population']"
          >Study Population - {{ numSubjects }}</v-chip
        >
      </v-toolbar-items>
    </v-toolbar>

    <v-flex>
      <v-container fill-height class="ma-0 pa-2">
        <v-select
          v-model="selVisitVariable"
          :items="visitItems"
          label="Select visit variable"
        >
        </v-select>

        <v-select
          v-model="selFirstVisit"
          :items="firstVisitEvents"
          label="Select first visit"
          :background-color="colors['firstVisit']"
          class="ml-2"
        >
        </v-select>

        <v-select
          v-model="selLastVisit"
          :items="lastVisitEvents"
          label="Select last visit"
          :background-color="colors['lastVisit']"
          class="ml-2"
        >
        </v-select>
        <v-spacer />
      </v-container>
    </v-flex>
  </section>
</template>

<script>
import axios from 'axios';
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dataSummary/types';
import { colors } from '@/utils/colors';

export default {
  data() {
    return {
      visitItems: ['Visit Event', 'Visit Number'],
      uniqueEvents: [],
      firstVisitEvents: [],
      lastVisitEvents: [],
      selVisitVariable: null,
      selFirstVisit: null,
      selLastVisit: null,
      numSubjects: 0,
      colors: colors,
    };
  },
  computed: {
    ...mapState('dataSummary', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      collection: state.COLLECTION,
      collectionSummaries: state.COLLECTION_SUMMARIES,
      firstVisit: state.FIRST_VISIT,
      lastVisit: state.LAST_VISIT,
      visitVariable: state.VISIT_VARIABLE,
      timesBetweenVisits: state.TIMES_BETWEEN_VISITS,
    }),
  },
  watch: {
    selVisitVariable(newval) {
      this.setVisitVariable(newval);
    },
    visitVariable() {
      this.selFirstVisit = null;
      this.selLastVisit = null;
      this.updateEvents();
    },
    firstVisit(fv) {
      this.selFirstVisit = fv;
      this.updateEvents();
    },
    lastVisit(lv) {
      this.selLastVisit = lv;
      this.updateEvents();
    },
    selFirstVisit(fv) {
      this.setFirstVisit(fv);
      this.updateTimesBetweenVisits();
    },
    selLastVisit(lv) {
      this.setLastVisit(lv);
      this.updateTimesBetweenVisits();
    },
    timesBetweenVisits() {
      var ns = 0;
      this.timesBetweenVisits.forEach(x => {
        ns += x.n_subjects;
      });
      this.numSubjects = ns;
    },
  },
  mounted() {
    this.selVisitVariable = this.visitVariable;
    this.selFirstVisit = this.firstVisit;
    this.selLastVisit = this.lastVisit;
    this.updateEvents();
  },
  methods: {
    updateEvents() {
      // Identify the unique events
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );

      if (!this.selFirstVisit) {
        this.setFirstVisit(this.uniqueEvents[0]);
      }
      if (!this.selLastVisit) {
        this.setLastVisit(this.uniqueEvents[this.uniqueEvents.length - 1]);
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
