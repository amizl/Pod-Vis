<template>
  <v-flex ref="container" fill-height style="display: inline-block">
    <svg ref="chart" :width="width" :height="height">
      <g ref="bars" :transform="`translate(${margin.left}, ${margin.top})`">
        <!-- Population bars are first so they will hide under cohort bars -->
        <rect
          v-for="(bin, i) in popBins"
          :key="`population-${i}`"
          :x="left ? xScale(bin.length) : 0"
          :y="yScale(bin.x1)"
          :height="
            yScale(bin.x0) - yScale(bin.x1) - 1 > 0
              ? yScale(bin.x0) - yScale(bin.x1) - 1
              : 0
          "
          :width="
            left
              ? w - xScale(bin.length) > 0
                ? w - xScale(bin.length)
                : 0
              : xScale(bin.length) > 0
              ? xScale(bin.length)
              : 0
          "
          fill="#A1A3AB"
          :opacity="getOpacity('population')"
        />
        <!-- Plot population minus selected cohort -->
        <animated-rect
          v-for="(bin, i) in popMinusBins"
          :key="`pop-minus-cohort-${i}`"
          :x="left ? xScale(bin.length) : 0"
          :y="yScale(bin.x1)"
          :height="
            yScale(bin.x0) - yScale(bin.x1) - 1 > 0
              ? yScale(bin.x0) - yScale(bin.x1) - 1
              : 0
          "
          :width="
            left
              ? w - xScale(bin.length) > 0
                ? w - xScale(bin.length)
                : 0
              : xScale(bin.length) > 0
              ? xScale(bin.length)
              : 0
          "
          fill="#3FB551"
          :opacity="getOpacity('non-cohort')"
         />
        <animated-rect
          v-for="(bin, i) in bins"
          :key="`cohort-${i}`"
          :x="left ? xScale(bin.length) : 0"
          :y="yScale(bin.x1)"
          :height="
            yScale(bin.x0) - yScale(bin.x1) - 1 > 0
              ? yScale(bin.x0) - yScale(bin.x1) - 1
              : 0
          "
          :width="
            left
              ? w - xScale(bin.length) > 0
                ? w - xScale(bin.length)
                : 0
              : xScale(bin.length) > 0
              ? xScale(bin.length)
              : 0
          "
          fill="#3F51B5"
          :opacity="getOpacity('cohort')"
        />

<!-- Cohort Mean -->
        <!-- <circle
          r="15"
          :cx="mean"
          :cy="h"
          fill="#3F51B5"
          stroke="#E8EAF6"
          stroke-width="5"
          fill-opacity=".9"
        /> -->
        <!-- Population Mean -->
        <!-- <circle
          r="15"
          :cx="populationMean"
          :cy="h"
          stroke="#3F51B5"
          fill="#E8EAF6"
          stroke-width="5"
          fill-opacity=".9"
        /> -->
        <g ref="brush" class="brush"></g>
      </g>

      <g
        v-xaxis="populationXAxis"
        :transform="`translate(${margin.left}, ${margin.top})`"
      ></g>
      <g
        v-yaxis="yAxis"
        :transform="
          `translate(${left ? width - margin.right : margin.left}, ${
            margin.top
          })`
        "
      ></g>
    </svg>
  </v-flex>
</template>

<script>
// Data Store
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
// D3 Modules
import { extent, max, mean, histogram } from 'd3-array';
import { brushY } from 'd3-brush';
import { select, event } from 'd3-selection';
import { scaleLinear } from 'd3-scale';
import 'd3-transition';
import { axisTop, axisLeft, axisRight } from 'd3-axis';
// Directives
import resize from 'vue-resize-directive';
// Components
import AnimatedRect from './HistogramBar.vue';

/**
 * Takes an array of key, value counts from crossfilter groups
 * and expands then flattens them. For example, [{key:5, value: 3}, {key:2, value: 2}]
 * would be flattened to [5,5,5,2,2]. This allows us to leverage d3's
 * histrogram/binning abilities.
 */
const flattenGroupCounts = data =>
  data.reduce((acc, curr) => {
    const { key: value, value: length } = curr;
    const arr = Array.from([].fill.call({ length }, value));
    return [...acc, ...arr];
  }, []);

export default {
  directives: {
    resize,
    xaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
      // .call(g => g.select('.domain').remove());
    },
    yaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
      // .call(g => g.select('.domain').remove());
    },
  },
  components: {
    AnimatedRect,
  },
  props: {
    id: {
      type: [Number, String],
      required: true,
    },
    dimensionName: {
      type: String,
      required: true,
    },
    left: {
      type: Boolean,
      default: false,
    },
    yDomain: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      isLoading: true,
      haveDimensions: false,
      width: 0,
      height: 0,
      margin: {
        top: 20,
        right: 25,
        bottom: 10,
        left: 25,
      },
      selected: [],
      container: null,
      dimension: null,
      group: [],
      data: [],
      populationData: [],
      selection: [],
    };
  },
  computed: {
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      dimensions: state.DIMENSIONS,
      highlightedSubset: state.HIGHLIGHTED_SUBSET,
    }),
    w() {
      const { left, right } = this.margin;
      const { width } = this;
      return width - left - right;
    },
    h() {
      const { top, bottom } = this.margin;
      const { height } = this;
      return height - top - bottom;
    },
    // colorScale() {
    //   return scaleOrdinal()
    //     .domain(this.data.map(c => c.key))
    //     .range(schemeCategory10);
    // },
    yScale() {
      return scaleLinear()
        .domain([0, this.yDomain])
        .range([this.h, 0]);
    },
    cohortXScale() {
      return scaleLinear()
        .domain(extent(this.data))
        .range([0, this.w]);
    },
    hist() {
      return histogram()
        .value(d => +d)
        .domain(this.yScale.domain())
        .thresholds(this.yScale.ticks(30));
    },
    popBins() {
      return this.hist(this.populationData);
    },
    bins() {
      return this.hist(this.data);
      // return histogram()
      //   .domain(this.xScale.domain())
      //   .thresholds(this.xScale.ticks(30))(this.data);
      // .domain(this.cohortXScale.domain())
      // .thresholds(this.cohortXScale.ticks(30))(this.data);
    },
    popMinusBins() {
      // subtract bins from population bins to get popMinusBins
      // i.e., bins for the non-cohort population
      var pb = this.hist(this.populationData);
      var b = this.hist(this.data);
      var pm_bins = [];
      var pb_len = pb.length;

      // TODO - compute this in a more straightforward fashion
      // TODO - factor out code in common with HistogramChart.vue
      for (var i = 0;i < pb_len; ++i) {
        var nbl = [];
	nbl.x0 = pb[i].x0;
	nbl.x1 = pb[i].x1;
        var bl = typeof(b[i]) !== 'undefined' ? b[i].length : 0;
	var pbl = typeof(pb[i]) !== 'undefined' ? pb[i].length : 0;
        // TODO - we're creating bins of the correct size for display
	// purposes, but the values inside aren't correct.
        for (var j = bl;j < pbl; ++j) {
	  nbl.push(1);
        }
        pm_bins.push(nbl);
      }
      return pm_bins;
    },
    mean() {
      return this.xScale(mean(this.data));
    },
    populationMean() {
      return this.xScale(mean(this.populationData));
    },
    xScale() {
      const yScale = scaleLinear()
        .domain([0, max(this.popBins, d => d.length)])
        .range(this.left ? [this.w, 0] : [0, this.w]);
      return yScale;
    },
    xAxis() {
      return axisTop(this.xScale);
    },
    populationXAxis() {
      return axisTop(this.xScale).ticks(3);
    },
    yAxis() {
      const axis = this.left ? axisRight : axisLeft;
      return axis(this.yScale);
    },
    brush() {
      return brushY()
        .extent([[0, 0], [this.w, this.h]])
        .on('start brush', this.brushed)
        .on('end', this.brushedData);
    },
    maxValueBetweenDimensions() {
      const firstMax = max(this.unfilteredData, d => d.firstVisit);
      const lastMax = max(this.unfilteredData, d => d.lastVisit);
      return Math.max(firstMax, lastMax);
    },
  },
  watch: {
    filteredData() {
      this.data = flattenGroupCounts(this.group.all());
      if (this.selected.length && !this.dimension.currentFilter()) {
        this.selected = [];
      }
    },
  },
  created() {
    const dimension = this.dimensions[this.dimensionName];
    this.dimension = dimension;
    this.populationData = this.unfilteredData.map(dimension.accessor);

    this.group = dimension.group();
    this.data = flattenGroupCounts(this.group.all());
  },
  mounted() {
    this.container = this.$refs.container;
    // Resize chart so we have parent dimensions (width/height)
    this.resizeChart();
    this.initializeBrush();
  },
  methods: {
    ...mapActions('cohortManager', {
      addFilter: actions.ADD_FILTER,
      clearFilter: actions.CLEAR_FILTER,
    }),
    initializeBrush() {
      const brushEl = this.$refs.brush;

      const brush = select(brushEl).call(this.brush);
      select(brushEl)
        .select('.selection')
        .attr('fill', '#3F51B5')
        .attr('fill-opacity', 0.1);

      // This provides the shape of our handles on the brush
      const handlePath = d => {
        const e = +(d.type == 'e'),
          x = e ? 1 : -1,
          y = this.h / 2;
        return `M${0.5 * x},${y}A6,6 0 0 ${e} ${6.5 * x},${y + 6}V${2 * y -
          6}A6,6 0 0 ${e} ${0.5 * x},${2 * y}ZM${2.5 * x},${y + 8}V${2 * y -
          8}M${4.5 * x},${y + 8}V${2 * y - 8}`;
      };

      const handle = brush
        .selectAll('.handle--custom')
        .data([{ type: 'w' }, { type: 'e' }])
        .enter()
        .append('path')
        .attr('class', 'handle--custom')
        .attr('fill', '#3F51B5')
        .attr('fill-opacity', 0.8)
        .attr('stroke', '#FFF')
        .attr('stroke-width', 1)
        .attr('cursor', 'ew-resize')
        .attr('d', handlePath)
        .attr('display', 'none');
      this.handle = handle;
    },
    /**
     * Gets the closest cohort bins to a selection so brush can appropriately
     * snap to the correct locations.
     */
    getClosestBins() {
      const selection = event.selection;
      const [low, high] = selection.map(this.yScale.invert);

      // Get closest bin to our lower selection
      const closestBinToLow = this.bins
        .map(bin => bin.x0)
        .map(x0 => Math.abs(x0 - low))
        .reduce((acc, currVal) => Math.min(acc, currVal));
      const newLowIdx = this.bins.findIndex(
        bin => Math.abs(bin.x0 - low) === closestBinToLow
      );
      const newLow = this.bins[newLowIdx].x0;
      // Get closest bin to our higher selection
      const closestBinToHigh = this.bins
        .map(bin => bin.x1)
        .map(x1 => Math.abs(x1 - high))
        .reduce((acc, currVal) => Math.min(acc, currVal));
      const newHighIdx = this.bins.findIndex(
        bin => Math.abs(bin.x1 - high) === closestBinToHigh
      );
      const newHigh = this.bins[newHighIdx].x1;

      return [newLow, newHigh].map(this.yScale);
    },
    brushedData() {
      // Only transition after input.
      if (!event.sourceEvent) return;
      // Ignore empty selections.
      if (!event.selection) {
        this.clearFilter({
          dimension: this.dimensionName,
        });
        return;
      }

      const [high, low] = this.getClosestBins();

      // Snap selections to closest bins
      select(this.$refs.brush)
        .transition()
        .call(event.target.move, [high, low]);

      const [invertedHigh, invertedLow] = [high, low].map(this.yScale.invert);

      // Filter dimension to be within snapped selection
      this.addFilter({
        dimension: this.dimensionName,
        filter: d => d >= invertedLow && d < invertedHigh,
      });

    },
    brushed() {
      const selection = event.selection;
      if (!selection) {
        this.selection = [];
        return; // Ignore empty selections
      }

      const [low, high] = selection;
      // Ignore selections with no range
      if (high - low === 0) {
        this.handle.attr('display', 'none');
        select(this.$refs.brush).call(this.brush.move, null);
        this.selection = [];
        return;
      }

      // Appropriately place brush handles
      // this.handle.attr('display', null).attr('transform', (d, i) => {
      //   return 'translate(' + selection[i] + ',' + -this.h / 8 + ')';
      // });

      // Set remap our selection to snap to closest bins
      this.selection = this.getClosestBins();
    },
    getFill(bin) {
      if (this.selection) {
        let [high, low] = this.selection.map(this.yScale.invert);
        let { x0, x1 } = bin;

        // Pad the high number as this might be a decimal
        // and can cause some bars to not be colored in range
        const PADDING = 1;
        // Check that bin is within selection range
        if (
          low - PADDING <= x0 &&
          low - PADDING <= x1 &&
          high + PADDING >= x0 &&
          high + PADDING >= x1
        ) {
          return '#3F51B5';
        } else {
          return '#E8EAF6';
        }
      } else {
        return '#3F51B5';
      }
    },
    getOpacity(subset) {
      if (this.highlightedSubset === 'None') {
        return 0.9;
      } else {
        if (this.highlightedSubset === subset) {
          return 1;
        } else {
	  return 0.3;
	}
      }
    },
    resizeChart() {
      const { height } = this.container.getBoundingClientRect();
      this.height = 200;
      this.width = 100;
      // this.height = height;
      // this.width = height / 3;
    },
  },
};
</script>

<style scoped></style>
