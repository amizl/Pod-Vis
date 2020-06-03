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
          :items="uniqueEvents"
          label="Select first visit"
          class="light-green"
        >
        </v-select>
        <v-spacer />
        <v-divider vertical class="ml-4"></v-divider>
        <v-select
          v-model="lastVisit"
          :items="uniqueEvents"
          label="Select last visit"
          class="light-blue"
        >
        </v-select>
      </v-toolbar-items>
      <v-spacer />
      <v-divider vertical class="ml-4"></v-divider>
    </v-toolbar>
    <v-divider></v-divider>
  </section>
</template>

<script>
import { mapState, mapMutations } from 'vuex';
import { state, actions } from '@/store/modules/dataSummary/types';

export default {
  data() {
    return {
      visitItems: ['Visit Event', 'Visit Number'],
      uniqueEvents: [],
      selVisitVariable: null,
    };
  },
  computed: {
    ...mapState('dataSummary', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
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
      },
    },
    firstVisit: {
      get() {
        return this.selFirstVisit;
      },
      set(value) {
        this.setFirstVisit(value);
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
