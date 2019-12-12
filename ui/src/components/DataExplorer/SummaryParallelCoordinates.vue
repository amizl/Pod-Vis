<template>
  <v-layout :key="chartsKey" :class="classes" fill-height>
    <v-flex
      v-for="(outcome, index) in outcomeVariables"
      :key="outcome.id"
      fill-height
      shrink
    >
      <v-layout fill-height>
        <v-flex fill-height>
          <parallel-coordinates :variable="outcome" />
        </v-flex>
        <v-flex v-if="index < outcomeVariables.length - 1" shrink>
          <v-divider vertical></v-divider>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dataExplorer/types';
import ParallelCoordinates from '@/components/DataExplorer/ParallelCoordinates.vue';

export default {
  components: {
    ParallelCoordinates,
  },
  data() {
    return {
      chartsKey: 0,
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      outcomeVariables: state.OUTCOME_VARIABLES,
    }),
    classes() {
      return {
        scrollable: true,
      };
    },
  },
  watch: {
    /**
     * Watch for user adding outcome variables. When this happens,
     * we want to trigger a rerender so all the charts' dimensions
     * resize according to the available space in the flex area.
     * We can achieve a forceful rerender by updating the key of
     * the parent component.
     */
    outcomeVariables() {
      this.rerenderCharts();
    },
  },
  methods: {
    rerenderCharts() {
      this.chartsKey += 1;
    },
  },
};
</script>

<style scoped>
.scrollable {
  overflow-x: auto;
}
.scrollable::-webkit-scrollbar {
  /* display: none; */
}
</style>
