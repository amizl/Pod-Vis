<template>
  <section>
    <v-toolbar card dense flat color="white rounded-lg">
      <!-- 
      <v-toolbar-items> <input-variables-dialog /> </v-toolbar-items>
      -->
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
          filled
          label="Select first visit"
        >
        </v-select>
        <v-spacer />
        <v-divider vertical class="ml-4"></v-divider>
        <v-select
          v-model="lastVisit"
          :items="uniqueEvents"
          outlined
          label="Select last visit"
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
  props: {
    visitVariable: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      visitItems: ['Visit Event', 'Visit Number'],
      uniqueEvents: [],
      selVisitVariable: '',
    };
  },
  computed: {
    ...mapState('dataSummary', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      collectionSummary: state.COLLECTION_SUMMARY,
      selFirstVisit: state.FIRST_VISIT,
      selLastVisit: state.LAST_VISIT,
    }),
    lastVisit: {
      get() {
        return this.selLastVisit;
      },
      set(value) {
        alert('In setter for last. New value: ' + value);
        this.setLastVisit(value);
      },
    },
    firstVisit: {
      get() {
        return this.selFirstVisit;
      },
      set(value) {
        alert('In setter for firstVisit. New value: ' + value);
        this.setFirstVisit(value);
      },
    },
  },
  watch: {
    selVisitVariable() {
      alert(
        'In watcher for visitVariable visit event changed to: ' +
          this.selVisitVariable
      );
      this.$emit('visitVarChanged', this.selVisitVariable);
    },
  },
  mounted() {
    // Identify the unique events
    this.uniqueEvents = this.getUniqueList(
      this.getColumn(this.collectionSummary, 0)
    );
    // this.visitVariable = this.visitItems[0];
    // this.firstVisit = this.uniqueEvents[0];
    // this.lastVisit = this.uniqueEvents[this.uniqueEvents.length - 1];
  },
  methods: {
    visitVarChanged: function(event) {
      console.log('Visit Event Changed to: ' + this.visitVariable);
      // `this` inside methods points to the Vue instance
      alert('Hello ' + event + '!');
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
