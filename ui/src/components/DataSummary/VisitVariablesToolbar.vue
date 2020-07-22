<template>
  <div>
    <v-app-bar
      dense
      flat
      color="rgb(247,216,206,0.5)"
      class="toolbar_step_highlight rounded-lg"
    >
      <v-toolbar-title class="primary--text title">
        CHOOSE FIRST & LAST VISIT
      </v-toolbar-title>

      <v-divider vertical class="ml-4 mr-4"> </v-divider>

      <v-chip color="primary" class="white--text title"
        >{{ collectionVarNames.length }} outcome variable<span
          v-if="collectionVarNames.length != 1"
          >s</span
        >&nbsp;selected</v-chip
      >
      <v-spacer />
      <v-chip
        :disabled="true"
        class="primary--text title"
        :style="'background: ' + colors['population'] + ';'"
        >Study Population - {{ numSelectedSubjects }}</v-chip
      >
    </v-app-bar>

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
  </div>
</template>

<script>
import axios from 'axios';
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dataSummary/types';
import { colors } from '@/utils/colors';
import {
  getObservationVariableIds,
  getObservationVariableNames,
} from '@/utils/helpers';

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
      firstVisits: state.FIRST_VISITS,
      lastVisits: state.LAST_VISITS,
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
        var varIds = getObservationVariableIds(this.collection);
        var lastVisit = null;
        varIds.forEach(vid => {
          var lv = this.lastVisits[vid];
          if (lastVisit == null) {
            lastVisit = lv;
          }
          // different variables have different visits
          else if (lastVisit != lv) {
            lastVisit = 'multiple';
          }
        });
        return lastVisit;
      },
      set(value) {
        if (value != 'multiple') {
          this.setLastVisit(value);
        }
      },
    },
    firstVisit: {
      get() {
        var varIds = getObservationVariableIds(this.collection);
        var firstVisit = null;
        varIds.forEach(vid => {
          var fv = this.firstVisits[vid];
          if (firstVisit == null) {
            firstVisit = fv;
          }
          // different variables have different visits
          else if (firstVisit != fv) {
            firstVisit = 'multiple';
          }
        });
        return firstVisit;
      },
      set(value) {
        if (value != 'multiple') {
          this.setFirstVisit(value);
        }
      },
    },
  },
  watch: {
    hideUnselectedVars(newval) {
      this.$emit('hideUnselectedVars', newval);
    },
    collectionSummaries(newval) {
      this.updateTimesBetweenVisits();
    },
    firstVisits(newval) {
      this.updateEvents();
      this.updateTimesBetweenVisits();
    },
    lastVisits(newval) {
      this.updateEvents();
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
      // TODO - ensure that these events are sorted chronologically
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );
      // HACK for PPMI
      if (
        this.uniqueEvents.join(',') ==
        'BL,PW,SC,ST,U01,V01,V02,V03,V04,V05,V06,V07,V08,V09,V10,V11,V12,V13,V14,V15,V16'
      ) {
        this.uniqueEvents = [
          'SC',
          'BL',
          'U01',
          'V01',
          'V02',
          'V03',
          'V04',
          'V05',
          'V06',
          'V07',
          'V08',
          'V09',
          'V10',
          'V11',
          'V12',
          'V13',
          'V14',
          'V15',
          'V16',
          'PW',
          'ST',
        ];
      }

      var varIds = getObservationVariableIds(this.collection);
      var firstLastVisit = null;
      var lastFirstVisit = null;
      var firstVisits = {};
      var lastVisits = {};

      varIds.forEach(v => {
        firstVisits[this.firstVisits[v]] = true;
        lastVisits[this.lastVisits[v]] = true;
      });

      this.uniqueEvents.forEach(e => {
        if (e in firstVisits) {
          lastFirstVisit = e;
        }
        if (firstLastVisit == null && e in lastVisits) {
          firstLastVisit = e;
        }
      });

      // possible first visit events - all those up until the first lastVisit
      this.firstVisitEvents = ['multiple'];
      for (var i = 0; i < this.uniqueEvents.length; i++) {
        if (this.lastVisit && this.uniqueEvents[i] == firstLastVisit) {
          break;
        }
        this.firstVisitEvents.push(this.uniqueEvents[i]);
      }

      // possible last visit events - starting after the last firstVisit
      var firstVisitSeen = !this.firstVisit;
      this.lastVisitEvents = ['multiple'];
      for (var i = 0; i < this.uniqueEvents.length; i++) {
        if (firstVisitSeen) {
          this.lastVisitEvents.push(this.uniqueEvents[i]);
        } else if (this.firstVisit && this.uniqueEvents[i] == lastFirstVisit) {
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
