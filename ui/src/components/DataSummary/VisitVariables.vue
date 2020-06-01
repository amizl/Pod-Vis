<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <visit-variables-toolbar
        :visit-variable="visitVariable"
        @visitVarChanged="propVisitVarChanged"
      ></visit-variables-toolbar>
      <v-container fluid fill-height class="pa-0 pb-1">
        <bubble-chart :visit-variable="visitVariable"> </bubble-chart>
      </v-container>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapMutations, mapState } from 'vuex';
import { mutations, state } from '@/store/modules/dataSummary/types';
import VisitVariablesToolbar from '@/components/DataSummary/VisitVariablesToolbar.vue';
import BubbleChart from '@/components/DataSummary/BubbleChart/BubbleChart.vue';

export default {
  components: {
    VisitVariablesToolbar,
    BubbleChart,
  },
  data() {
    return {
      visitVariable: 'Not Set',
    };
  },
  computed: {
    ...mapState('dataSummary', {
      isLoading: state.IS_LOADING,
      collection: state.COLLECTION,
      collection_summary: state.COLLECTION_SUMMARY,
    }),
  },
  methods: {
    propVisitVarChanged(newVisitVar) {
      alert('In parent. Visit var changed: ' + newVisitVar);
      this.visitVariable = newVisitVar;
    },
  },
};
</script>
