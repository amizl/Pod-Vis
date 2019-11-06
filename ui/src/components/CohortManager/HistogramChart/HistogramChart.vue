<template>
  <v-flex ref="container">
    <svg ref="chart" :width="width" :height="height">
      <g ref="bars" :transform="`translate(${margin.left}, ${margin.top})`">
        <!-- Population bars are first so they will hide under cohort bars -->
        <rect
          v-for="(bin, i) in popBins"
          :key="`population-${i}`"
          :x="xScale(bin.x0)"
          :y="yScale(bin.length)"
          :width="
            xScale(bin.x1) - xScale(bin.x0) - 1 > 0
              ? xScale(bin.x1) - xScale(bin.x0) - 1
              : 0
          "
          :height="h - yScale(bin.length) > 0 ? h - yScale(bin.length) : 0"
          fill="#F8D580"
          :opacity="getOpacity('population')"
        />
        <rect v-if="highlightedSubset === 'non-cohort'"
          v-for="(bin, i) in popMinusBins"
          :key="`pop-minus-cohort-${i}`"
          :x="xScale(bin.x0)"
          :y="getNonCohortY(bin)"
          :width="
            xScale(bin.x1) - xScale(bin.x0) - 1 > 0
              ? xScale(bin.x1) - xScale(bin.x0) - 1
              : 0
          "
	  :height="getNonCohortHeight(bin)"
	  fill="#3FB551"
          :opacity="getOpacity('non-cohort')"
        />
        <rect v-if="highlightedSubset === 'cohort'"
          v-for="(bin, i) in bins"
          :key="`cohort-${i}`"
          :x="xScale(bin.x0)"
          :y="getCohortY(bin)"
          :width="
            xScale(bin.x1) - xScale(bin.x0) - 1 > 0
              ? xScale(bin.x1) - xScale(bin.x0) - 1
              : 0
          "
          :height="getCohortHeight(bin)"
          fill="#3F51B5"
          :opacity="getOpacity('cohort')"
        />
        <!-- Cohort Mean -->
        <circle v-if="typeof(mean) !== 'undefined'"
          r="7"
          :cx="mean"
          :cy="h"
          fill="blue"
	  stroke="#3696f8"
          stroke-width="1"
          fill-opacity=".6"
        />
        <!-- Population Mean -->
        <circle v-if="typeof(populationMean) !== 'undefined'"
          r="7"
          :cx="populationMean"
          :cy="h"
          stroke="#f8d537"
          fill="#F88123"
          stroke-width="1"
          fill-opacity=".8"
        />
        <g ref="brush" class="brush"></g>
      </g>

      <g
        v-xaxis="populationXAxis"
        :transform="`translate(${margin.left},${h + margin.top})`"
      ></g>
      <g
        v-yaxis="yAxis"
        :transform="`translate(${margin.left}, ${margin.top})`"
      ></g>
    </svg>
  </v-flex>
</template>

<script>
// Data Store
import { mapState, mapActions, mapGetters } from 'vuex';
import { state, getters, actions } from '@/store/modules/cohortManager/types';
// D3 Modules
import { extent, max, mean, histogram } from 'd3-array';
import { brushX } from 'd3-brush';
import { select, event } from 'd3-selection';
import { scaleLinear } from 'd3-scale';
import 'd3-transition';
import { axisBottom, axisLeft } from 'd3-axis';
// Directives
import resize from 'vue-resize-directive';
// Components
//import AnimatedRect from './HistogramBar.vue';

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
        // .transition()
        .call(axisMethod);
      // .call(g => g.select('.domain').remove());
    },
    yaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        // .transition()
        .call(axisMethod);
      // .call(g => g.select('.domain').remove());
    },
  },
  components: {
//    AnimatedRect,
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
    population: {
      type: Boolean,
      default: false,
    },
    inputVariable: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isLoading: true,
      haveDimensions: false,
      width: 0,
      height: 0,
      margin: {
        top: 10,
        right: 30,
        bottom: 20,
        left: 50,
      },
      selected: [],
      container: null,
      dimension: null,
      group: [],
      data: [],
      populationData: [],
      selection: [],
      populationCounts: {}
    };
  },
  computed: {
    ...mapGetters('cohortManager', {
      findCohortQuery: getters.FIND_COHORT_QUERY,
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      dimensions: state.DIMENSIONS,
      highlightedSubset: state.HIGHLIGHTED_SUBSET,
      cohort: state.COHORT,
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
    xScale() {
      return scaleLinear()
        .domain(extent(this.populationData))
        .range([0, this.w]);
    },
    cohortXScale() {
      return scaleLinear()
        .domain(extent(this.data))
        .range([0, this.w]);
    },
    hist() {
      return histogram()
        .value(d => +d)
        .domain(this.xScale.domain())
        .thresholds(this.xScale.ticks(30));
    },
    popBins() {
      var pop_bins = this.hist(this.populationData);
      // cache bin counts
      this.populationCounts = {};
      var pb_len = pop_bins.length;
      for (var i = 0;i < pb_len; ++i) {
        this.populationCounts[pop_bins[i].x0] = pop_bins[i].length;
      }
      return pop_bins;
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
      // TODO - factor out code in common with VerticalHistogram.vue
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
      return this.xScale(
        mean(this.filteredData.map(this.dimension.accessor))
      );
    },
    populationMean() {
      return this.xScale(mean(this.populationData));
    },
    yScale() {
      const yScale = scaleLinear()
        .domain([0, max(this.popBins, d => d.length)])
        .range([this.h, 0]);
      return yScale;
    },
    xAxis() {
      return axisBottom(this.xScale);
    },
    populationXAxis() {
      return axisBottom(this.xScale);
    },
    yAxis() {
      return axisLeft(this.yScale).ticks(3);
    },
    brush() {
      return brushX()
        .extent([[0, 0], [this.w, this.h]])
        .on('start brush', this.brushed)
        .on('end', this.brushedData);
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

    if (this.inputVariable && this.hasUserSelectedCohort) {
      // there should only be one query for a histogram...
      const [query] = this.findCohortQuery(this.dimensionName);

      if (typeof(query) !== 'undefined') {
        this.$nextTick(() => {
          const minValue = query.min_value;
          const maxValue = query.max_value;
          // Snap selections to closest bins
          select(this.$refs.brush).call(this.brush.move, [
            this.xScale(minValue),
            this.xScale(maxValue),
          ]);

          // Filter dimension to be within snapped selection
          this.addFilter({
            dimension: this.dimensionName,
            filter: d => d >= minValue && d < maxValue,
            query: {
              minValue,
              maxValue,
            },
          });
        });
      }
    }
  },
  destroyed() {
    this.clearFilter({
      dimension: this.dimensionName,
    });
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
      const [low, high] = selection.map(this.xScale.invert);

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

      return [newLow, newHigh].map(this.xScale);
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

      const [low, high] = this.getClosestBins();
//      console.log("closest bins low = " low.x0 + "-" + low.x1 + " high = " + high.x0 + "-" + high.x1);
//      console.log("closest bins low = " + low + " high = " + high);

      // Snap selections to closest bins
      select(this.$refs.brush)
        .transition()
        .call(event.target.move, [low, high]);

      const [invertedLow, invertedHigh] = [low, high].map(this.xScale.invert);

      // Filter dimension to be within snapped selection
      this.addFilter({
        dimension: this.dimensionName,
        filter: d => d >= invertedLow && d < invertedHigh,
        query: {
          minValue: invertedLow,
          maxValue: invertedHigh,
        },
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
      this.handle.attr('display', null).attr('transform', (d, i) => {
        return 'translate(' + selection[i] + ',' + -this.h / 4 + ')';
      });

      // Set remap our selection to snap to closest bins
      this.selection = this.getClosestBins();
    },
    hasSelection() {
      if (this.selection) {
        if (this.selection.length) {
          return true;
	}
      }
      return false;
    },
    isBinSelected(bin) {
      let [low, high] = this.selection.map(this.xScale.invert);
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
        return true;
      }
      return false;
    },
    getCohortY(bin) {
        if (this.isBinSelected(bin)) {
//     console.log("getCohortY() binx0=" + bin.x0 + " selected=" + this.isBinSelected(bin));
     }
     var y = this.yScale(bin.length);
     if (this.hasSelection()) {
        return this.isBinSelected(bin) ? y : this.yScale(0);
      } else {
        return y;
      }
    },
    getCohortHeight(bin) {
    if (this.isBinSelected(bin)) {
//      console.log("getCohortHeight() binx0=" + bin.x0 + " selected=" + this.isBinSelected(bin));
      }
var bar_height = this.h - this.yScale(bin.length) > 0 ? this.h - this.yScale(bin.length) : 0;
      if (this.hasSelection()) {
        return this.isBinSelected(bin) ? bar_height : 0;
      } else {
        return bar_height;
      }
    },
    getNonCohortY(bin) {
      var y = this.yScale(bin.length)
      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
	  return y;
	} else {
	   var bin_len = this.populationCounts[bin.x0];
	   return this.yScale(bin_len);
        }
      } else {
        return y;
      }
    },
    getNonCohortHeight(bin) {
      var bar_height = this.h - this.yScale(bin.length) > 0 ? this.h - this.yScale(bin.length) : 0;
      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
	  return bar_height;
	} else {
	   var bin_len = this.populationCounts[bin.x0];
	   return this.h - this.yScale(bin_len) > 0 ? this.h - this.yScale(bin_len) : 0;
        }
      } else {
        return bar_height;
      }
    },
    getOpacity(subset) {
      return 0.7;
    },
    resizeChart() {
      this.height = 100;
      this.width = 350;
    },
  },
};
</script>

<style scoped></style>
