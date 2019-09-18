<template>
  <v-sheet
    color="white"
    height="100%"
    min-height="250px"
    min-width="200px"
    :class="classed"
    @click="selectForDetailedView"
  >
    <v-layout column fill-height>
      <v-card-title class="subheading primary--text text--darken-4">
        {{
          variable.type == 'observation'
            ? `${variable.parentLabel} - ${variable.label}`
            : variable.label
        }}
        <v-spacer />
      </v-card-title>
      <parallel-coordinates-chart
        :variable="variable"
        :dimension-name="variable.id"
      />
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';
import ParallelCoordinatesChart from '@/components/DataExplorer/ParallelCoordinatesChart.vue';

export default {
  components: {
    ParallelCoordinatesChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      toggled: false,
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      detailedView: state.DETAILED_VIEW,
    }),
    /**
     * A chart is toggled if there is currently an item toggled and that
     * item's id is equal to this component's.
     */
    isToggled() {
      return this.detailedView && this.detailedView.id === this.variable.id;
    },
    classed() {
      return {
        'elevation-4': this.isToggled,
        'pa-1': this.isToggled,
        'zoom-in': !this.isToggled,
        'zoom-out': this.isToggled,
        // We want to fade elements that are not selected
        // only when there is currently an element selected.
        fade: this.detailedView && !this.isToggled,
      };
    },
  },
  created() {},
  methods: {
    ...mapActions('dataExplorer', {
      setDetailedView: actions.SET_DETAILED_VIEW,
    }),
    selectForDetailedView() {
      if (this.isToggled) {
        this.setDetailedView(null);
      } else {
        this.setDetailedView(this.variable);
      }
    },
  },
};
</script>

<style scoped>
.zoom-in {
  cursor: zoom-in;
}
.zoom-out {
  cursor: zoom-out;
}
.fade {
  opacity: 0.5;
}
</style>
