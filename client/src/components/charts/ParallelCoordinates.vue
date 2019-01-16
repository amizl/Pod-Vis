<template>
  <div class="parcoords" style="width:100%;height:500px"></div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohort/types';
import ParCoords from 'parcoord-es';
import { selectAll } from 'd3-selection';
// import { scaleOrdinal } from 'd3-scale';
// import { schemeCategory10 } from 'd3-scale-chromatic';

export default {
  props: {
    data: {
      type: Array,
      required: false,
      default: () => [
        { name: 'Asparagus', protein: 2.2, calcium: 0.024, sodium: 0.002 },
        { name: 'Butter', protein: 0.85, calcium: 0.024, sodium: 0.714 },
        { name: 'Coffeecake', protein: 6.8, calcium: 0.054, sodium: 0.351 },
        { name: 'Pork', protein: 28.5, calcium: 0.016, sodium: 0.056 },
        { name: 'Provolone', protein: 25.58, calcium: 0.756, sodium: 0.876 },
      ],
    },
    ticks: {
      type: Boolean,
      required: false,
      default: true,
    },
    color: {
      type: String,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      chart: null,
      context: this.data, // all data
      focus: [], // data filtered by brushing
      brushed: [], // Mapping of axes and their ranges/values within brush
      margin: { top: 50, right: 25, bottom: 50, left: 25 },
      brushMode: '1D-axes',
      mode: 'queue',
      alphaOnBrushed: 0.1,
    };
  },
  computed: {
    ...mapState('cohort', {
      cohortSelection: state.COHORT_SELECTION,
    }),
  },
  mounted() {
    this.chart = ParCoords()(this.$el);

    this.chart
      .data(this.context)
      .margin(this.margin)
      .render()
      .createAxes()
      .brushMode(this.brushMode)
      .mode(this.mode)
      .alphaOnBrushed(this.alphaOnBrushed)
      .interactive()
      .reorderable();

    if (!this.ticks) this.hideTicks();

    this.setChartListeners();
  },
  methods: {
    ...mapActions('cohort', {
      setCohortSelection: actions.SET_COHORT_SELECTION,
    }),
    hideTicks() {
      selectAll('.axis g').style('display', 'none');
      selectAll('.axis path').style('display', 'none');
    },
    showTicks() {
      selectAll('.axis g').style('display', 'block');
      selectAll('.axis path').style('display', 'block');
    },
    setChartListeners() {
      // Listen on the brushend so there are not hundreds
      // of events fired when moving brush along dimension
      this.chart.on('brushend', (brushed, args) => {
        // args can be null if there are no elements
        // within bounds of the brush
        if (args) {
          this.brushed = brushed;

          const { axis } = args;
          const { scaled } = args.selection;
          // this.cohortSelection[axis] = scaled;
          this.setCohortSelection({ axis, scaled });
        }
      });
    },
  },
};
</script>

<style scoped>
.selection {
  background-color: black;
}
</style>
