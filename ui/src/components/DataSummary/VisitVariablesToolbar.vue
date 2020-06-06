L<template>
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
          v-model="selFirstVisit"
          :items="firstVisitEvents"
          label="Select first visit"
          :background-color="colors['firstVisit']"
        >
        </v-select>
        <v-spacer />
        <v-divider vertical class="ml-4"></v-divider>
        <v-select
          v-model="selLastVisit"
          :items="lastVisitEvents"
          label="Select last visit"
          :background-color="colors['lastVisit']"
        >
        </v-select>
      </v-toolbar-items>
      <v-spacer />
      <v-divider vertical class="ml-4"></v-divider>
    </v-toolbar>
    <v-divider></v-divider>

    <v-data-table
      :headers="headers"
      :items="timesBetweenVisits"
      dense
      hide-default-header
      hide-actions
      :pagination.sync="pagination"
    >
      <template v-slot:items="props">
        <tr>
          <td class="text-xs-left">{{ props.item.study_name }}</td>
          <td class="text-xs-left">{{ props.item.n_subjects }}</td>
          <td class="text-xs-left">
            {{ props.item.avg_time_secs | formatTime }}
          </td>
        </tr>
      </template>
    </v-data-table>
  </section>
</template>

<script>
import axios from 'axios';
import { mapState, mapMutations } from 'vuex';
import { state, actions } from '@/store/modules/dataSummary/types';
import { colors } from '@/utils/colors';
import { format } from 'd3-format';

export default {
  filters: {
    formatTime(tsecs) {
      var tdays = tsecs / (3600 * 24);
      var tyears = tdays / 365.25;
      if (tdays <= 60) {
        return format('.1f')(tdays) + ' days';
      } else {
        return format('.1f')(tyears) + ' years';
      }
    },
  },
  data() {
    return {
      visitItems: ['Visit Event', 'Visit Number'],
      uniqueEvents: [],
      firstVisitEvents: [],
      lastVisitEvents: [],
      selVisitVariable: null,
      selFirstVisit: null,
      selLastVisit: null,
      timesBetweenVisits: [],
      colors: colors,
      headers: [
        {
          text: 'Study',
          align: 'left',
          sortable: true,
          value: 'study_name',
        },
        {
          text: 'Subject Count',
          align: 'left',
          sortable: true,
          value: 'n_subjects',
        },
        {
          text: 'Average Time',
          align: 'left',
          sortable: true,
          value: 'avg_time_secs',
        },
      ],
      pagination: {
        rowsPerPage: -1,
      },
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
    }),
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
    firstVisit(fv) {
      this.selFirstVisit = fv;
    },
    lastVisit(lv) {
      this.selLastVisit = lv;
    },
    selFirstVisit(fv) {
      this.setFirstVisit(fv);
      this.updateTimesBetweenVisits();
    },
    selLastVisit(lv) {
      this.setLastVisit(lv);
      this.updateTimesBetweenVisits();
    },
  },
  created() {
    this.selVisitVariable = this.visitVariable;
    this.selFirstVisit = this.firstVisit;
    this.selLastVisit = this.lastVisit;
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

      if (!this.firstVisit) {
        this.selFirstVisit = this.uniqueEvents[0];
      }
      if (!this.lastVisit) {
        this.selLastVisit = this.uniqueEvents[this.uniqueEvents.length - 1];
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
    async updateTimesBetweenVisits() {
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
          this.timesBetweenVisits = data['times'];
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
