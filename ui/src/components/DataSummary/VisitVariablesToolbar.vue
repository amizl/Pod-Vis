<template>
  <section>
    <v-toolbar card dense flat color="white rounded-lg">
      <v-toolbar-items>
        <v-select
          v-model="selVisitVariable"
          :items="visitItems"
          label="Select visit variable"
        >
        </v-select>
        <v-spacer />
        <v-divider vertical class="ml-4"></v-divider>
        <v-select
          v-model="firstVisit"
          :items="firstVisitEvents"
          label="Select first visit"
          :background-color="colors['firstVisit']"
        >
        </v-select>
        <v-spacer />
        <v-divider vertical class="ml-4"></v-divider>
        <v-select
          v-model="lastVisit"
          :items="lastVisitEvents"
          label="Select last visit"
          :background-color="colors['lastVisit']"
        >
        </v-select>
        &nbsp; Average time between visits: {{ timeBetweenVisits }}
      </v-toolbar-items>
      <v-spacer />
      <v-divider vertical class="ml-4"></v-divider>
    </v-toolbar>
    <v-divider></v-divider>
  </section>
</template>

<script>
import axios from 'axios';
import { mapState, mapMutations } from 'vuex';
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
      timeBetweenVisits: 'N/A',
      colors: colors,
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
      visitVariable: state.VISIT_VARIABLE,
    }),
    lastVisit: {
      get() {
        return this.selLastVisit;
      },
      set(value) {
        this.setLastVisit(value);
        this.updateEvents();
      },
    },
    firstVisit: {
      get() {
        return this.selFirstVisit;
      },
      set(value) {
        this.setFirstVisit(value);
        this.updateEvents();
      },
    },
  },
  watch: {
    selVisitVariable(newval) {
      this.setVisitVariable(newval);
      this.setFirstVisit(null);
      this.setLastVisit(null);
    },
    visitVariable() {
      this.updateEvents();
    },
    selFirstVisit() {
      this.updateTimeBetweenVisits();
    },
    selLastVisit() {
      this.updateTimeBetweenVisits();
    },
  },
  created() {
    this.selVisitVariable = this.visitVariable;
  },
  mounted() {
    this.updateEvents();
  },
  methods: {
    updateEvents() {
      // Identify the unique events
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );
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
    async updateTimeBetweenVisits() {
      if (this.selFirstVisit && this.selLastVisit) {
        var query_by =
          this.visitVariable === 'Visit Event' ? 'visit_event' : 'visit_num';
        var request_url =
          '/api/collections/time_between_visits/' +
          this.collection.id +
          '?query_by=' +
          query_by +
          '&visit1=' +
          this.selFirstVisit +
          '&visit2=' +
          this.selLastVisit;
        const { data } = await axios.get(request_url);
        if (
          data['query_by'] === query_by &&
          data['visit1'] == this.selFirstVisit &&
          data['visit2'] == this.selLastVisit
        ) {
          this.timeBetweenVisits =
            data['times'][0]['avg_time_secs'] / (3600 * 24.0) / 365.0 +
            ' years';
        }
      }
    },
    ...mapMutations('dataSummary', {
      setFirstVisit: actions.SET_FIRST_VISIT,
      setLastVisit: actions.SET_LAST_VISIT,
      setVisitVariable: actions.SET_VISIT_VARIABLE,
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
