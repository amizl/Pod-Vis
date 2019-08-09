<template>
  <v-flex ref="container" fill-height>
    <svg ref="chart" :width="width" :height="height">
      <g ref="bars" :transform="`translate(${margin.left}, ${margin.top})`">
        <!-- Population bars are first so they will hide under cohort bars -->
        <rect
          v-for="(bin, i) in popBins"
          :key="`population-${i}`"
          :x="xScale(bin.x0)"
          :y="yScale(bin.length)"
          :width="xScale(bin.x1) - xScale(bin.x0) - 1"
          :height="h - yScale(bin.length)"
          fill="#E8EAF6"
        />

        <animated-rect
          v-for="(bin, i) in bins"
          :key="`cohort-${i}`"
          :x="xScale(bin.x0)"
          :y="yScale(bin.length)"
          :width="xScale(bin.x1) - xScale(bin.x0) - 1"
          :height="h - yScale(bin.length)"
          :fill="selection.length ? getFill(bin) : '#3F51B5'"
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
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
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
    population: {
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
    };
  },
  computed: {
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      dimensions: state.DIMENSIONS,
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
    mean() {
      return this.xScale(mean(this.data));
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
      }

      const [low, high] = this.getClosestBins();

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
    getFill(bin) {
      if (this.selection) {
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
          return '#3F51B5';
        } else {
          return '#E8EAF6';
        }
      } else {
        return '#3F51B5';
      }
    },
    resizeChart() {
      const { width, height } = this.container.getBoundingClientRect();
      this.width = width;
      this.height = height;
    },
  },
};
</script>

<style scoped></style>
