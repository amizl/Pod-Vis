<template>
  <div ref="container" fill-height style="display: inline-block">
    <svg ref="chart" :width="width" :height="height">
      <g ref="bars" :transform="`translate(${margin.left}, ${margin.top})`">
        <title v-if="hasSelection()">
          Click outside the selected area to remove the filter.
        </title>
        <title v-else>Click and drag to add a cohort filter.</title>
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
          :fill="colors['population']"
          :opacity="getOpacity('population')"
        />
        <!-- Plot population minus selected cohort -->
        <rect
          v-for="(bin, i) in popMinusBins"
          v-if="highlightedSubset === 'non-cohort'"
          :key="`pop-minus-cohort-${i}`"
          :x="getNonCohortX(left, bin)"
          :y="yScale(bin.x1)"
          :height="
            yScale(bin.x0) - yScale(bin.x1) - 1 > 0
              ? yScale(bin.x0) - yScale(bin.x1) - 1
              : 0
          "
          :width="getNonCohortWidth(left, bin)"
          :fill="colors['nonCohort']"
          :opacity="getOpacity('non-cohort')"
        />
        <rect
          v-for="(bin, i) in bins"
          v-if="highlightedSubset === 'cohort'"
          :key="`cohort-${i}`"
          :x="getCohortX(left, bin)"
          :y="yScale(bin.x1)"
          :height="
            yScale(bin.x0) - yScale(bin.x1) - 1 > 0
              ? yScale(bin.x0) - yScale(bin.x1) - 1
              : 0
          "
          :width="getCohortWidth(left, bin)"
          :fill="colors['cohort']"
          :opacity="getOpacity('cohort')"
        />

        <!-- Cohort Mean -->
        <circle
          v-if="typeof mean !== 'undefined'"
          r="7"
          :cx="left ? w : 0"
          :cy="mean"
          :fill="colors['cohort-circle-fill']"
          :stroke="colors['cohort-circle-stroke']"
          :stroke-width="colors['cohort-circle-stroke-width']"
          :fill-opacity="colors['cohort-circle-fill-opacity']"
        >
          <title>Cohort mean value</title>
        </circle>
        <!-- Population Mean -->
        <circle
          v-if="typeof populationMean !== 'undefined'"
          r="7"
          :cx="left ? w : 0"
          :cy="populationMean"
          :fill="colors['population-circle-fill']"
          :stroke="colors['population-circle-stroke']"
          :stroke-width="colors['population-circle-stroke-width']"
          :fill-opacity="colors['population-circle-fill-opacity']"
        >
          <title>Population mean value</title>
        </circle>
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
  </div>
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
// import AnimatedRect from './HistogramBar.vue';
import { colors } from '@/utils/colors';

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
    left: {
      type: Boolean,
      default: false,
    },
    yMin: {
      type: Number,
      required: true,
    },
    yDomain: {
      type: Number,
      required: true,
    },
    variable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isLoading: true,
      haveDimensions: false,
      width: 0,
      height: 0,
      filter: undefined,
      selected: [],
      container: null,
      dimension: null,
      group: [],
      data: [],
      populationData: [],
      selection: [],
      populationCounts: {},
      mean: undefined,
      populationMean: undefined,
      colors: colors,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      dimensions: state.DIMENSIONS,
      highlightedSubset: state.HIGHLIGHTED_SUBSET,
    }),
    num_bins() {
      if (this.variable.value_type === 'decimal' && this.yDomain < 30) {
        return this.yDomain + 1;
      } else {
        return 30;
      }
    },
    margin() {
      return {
        top: 20,
        right: this.left ? 30 : 10,
        bottom: 10,
        left: this.left ? 10 : 30,
      };
    },
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
        .domain([this.yMin, this.yDomain])
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
        .thresholds(this.yScale.ticks(this.num_bins));
    },
    popBins() {
      const popBins = this.hist(this.populationData);
      // cache bin counts
      this.populationCounts = {};
      const pbLen = popBins.length;
      for (let i = 0; i < pbLen; i += 1) {
        this.populationCounts[popBins[i].x0] = popBins[i].length;
      }
      return popBins;
    },
    bins() {
      return this.hist(this.data);
    },
    popMinusBins() {
      // subtract bins from population bins to get popMinusBins
      // i.e., bins for the non-cohort population
      const pb = this.hist(this.populationData);
      const b = this.hist(this.data);
      const pmBins = [];
      const pbLen = pb.length;

      // TODO - compute this in a more straightforward fashion
      // TODO - factor out code in common with HistogramChart.vue
      for (let i = 0; i < pbLen; i += 1) {
        const nbl = [];
        nbl.x0 = pb[i].x0;
        nbl.x1 = pb[i].x1;
        const bl = typeof b[i] !== 'undefined' ? b[i].length : 0;
        const pbl = typeof pb[i] !== 'undefined' ? pb[i].length : 0;
        // TODO - we're creating bins of the correct size for display
        // purposes, but the values inside aren't correct.
        for (let j = bl; j < pbl; j += 1) {
          nbl.push(1);
        }
        pmBins.push(nbl);
      }
      return pmBins;
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
      this.updateSelected();
      this.updateMean();
    },
    selected(newSel) {
      // prevent loop
      if (!newSel.length) {
        return;
      }

      // check whether selection has been cleared, remove brush if so
      if (this.hasSelection()) {
        // assess whether the filter on our dimension has been cleared
        const dim = this.dimensions[this.dimensionName];
        if (typeof dim === 'undefined') {
          this.clearSelection();
        } else {
          const cf = dim.currentFilter();
          if (typeof cf === 'undefined') {
            this.clearSelection();
          }
        }
      }
      this.updateMean();
    },
    populationData() {
      this.updatePopulationMean();
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
    clearSelection() {
      this.handle.attr('display', 'none');
      select(this.$refs.brush).call(this.brush.move, null);
      this.selected = [];
    },
    updateSelected() {
      if (this.hasSelection()) {
        const f = this.filter;
        const accFn = this.dimension.accessor;
        const filtered = this.filteredData.filter(d => {
          const datum = accFn(d);
          return f.filter(datum);
        });
        this.selected = filtered.map(accFn);
      }
    },
    updateMean() {
      // current selection (if any) must be taken into account
      if (this.hasSelection()) {
        this.mean = this.yScale(mean(this.selected));
      } else {
        this.mean = this.yScale(mean(this.data));
      }
    },
    updatePopulationMean() {
      this.populationMean = this.yScale(mean(this.populationData));
    },
    userChangedVariable() {
      this.$emit('userChangedVariable', this.dimensionName);
    },
    initializeBrush() {
      const brushEl = this.$refs.brush;

      const brush = select(brushEl).call(this.brush);
      select(brushEl)
        .select('.selection')
        .attr('fill', '#3F51B5')
        .attr('fill-opacity', 0.1);

      // This provides the shape of our handles on the brush
      const handlePath = d => {
        const e = +(d.type === 'e');
        const x = e ? 1 : -1;
        const y = this.w;
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
      const { selection } = event;
      const [upper, lower] = selection.map(this.yScale.invert);
      // TODO - this does not yet support flip_axis
      // Get closest bin to our upper selection (i.e., higher up on the screen)
      const closestBinToUpper = this.bins
        .map(bin => bin.x1)
        .map(x1 => Math.abs(x1 - upper))
        .reduce((acc, currVal) => Math.min(acc, currVal));
      const newUpperIdx = this.bins.findIndex(
        bin => Math.abs(bin.x1 - upper) === closestBinToUpper
      );
      const newUpper = this.bins[newUpperIdx].x1;

      // Get closest bin to our lower selection (i.e., lower down on the screen)
      const closestBinToLower = this.bins
        .map(bin => bin.x0)
        .map(x0 => Math.abs(x0 - lower))
        .reduce((acc, currVal) => Math.min(acc, currVal));
      const newLowerIdx = this.bins.findIndex(
        bin => Math.abs(bin.x0 - lower) === closestBinToLower
      );
      const newLower = this.bins[newLowerIdx].x0;
      return [newUpper, newLower].map(this.yScale);
    },
    brushedData() {
      // Only transition after input.
      if (!event.sourceEvent) return;
      // Ignore empty selections.
      if (!event.selection) {
        this.selected = [];
        this.clearFilter({
          dimension: this.dimensionName,
        });
        this.filter = undefined;
        return;
      }
      const [high, low] = this.getClosestBins();

      // Snap selections to closest bins
      select(this.$refs.brush)
        .transition()
        .call(event.target.move, [high, low]);

      var [invertedHigh, invertedLow] = [high, low].map(this.yScale.invert);

      // workaround for when entire range is selected
      var last_bin = this.bins[this.bins.length - 1];
      if (last_bin.x0 == last_bin.x1) {
        last_bin = this.bins[this.bins.length - 2];
      }
      if (invertedHigh >= last_bin.x1) {
        // add a small amount so nobody notices
        invertedHigh += (last_bin.x1 - last_bin.x0) * 0.1;
      }

      // Filter dimension to be within snapped selection
      const newFilter = {
        dimension: this.dimensionName,
        filter: d => d >= invertedLow && d < invertedHigh,
        query: {
          minValue: invertedLow,
          maxValue: invertedHigh,
        },
      };
      this.addFilter(newFilter);
      // assumes at most 1 filter, which appears to be the case
      this.filter = newFilter;
      this.updateSelected();
      this.$emit('userChangedVariable', this.dimensionName);
    },
    brushed() {
      const { selection } = event;
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
      var tx = this.w * 2;
      this.handle
        .attr('display', null)
        .attr(
          'transform',
          (d, i) => `translate(${tx},${selection[i]}) rotate(90)`
        );

      // Set remap our selection to snap to closest bins
      this.selection = this.getClosestBins();
    },
    getFill(bin) {
      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
          return '#3F51B5';
        }
        return '#E8EAF6';
      }
      return '#3F51B5';
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
      const [high, low] = this.selection.map(this.yScale.invert);
      const { x0, x1 } = bin;

      // padding must be adaptive - set to half the bin width/height
      const PADDING = (x1 - x0) / 2.0;
      // Check that bin is within selection range
      if (low - PADDING <= x0 && high + PADDING >= x1) {
        return true;
      }
      return false;
    },
    getCohortX(left, bin) {
      const x = left ? this.xScale(bin.length) : 0;
      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
          return x;
        }
        return left ? this.xScale(0) : 0;
      }
      return x;
    },
    getCohortWidth(left, bin) {
      const barWidth = left
        ? this.w - this.xScale(bin.length) > 0
          ? this.w - this.xScale(bin.length)
          : 0
        : this.xScale(bin.length) > 0
        ? this.xScale(bin.length)
        : 0;

      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
          return barWidth;
        }
        return 0;
      }
      return barWidth;
    },
    getNonCohortX(left, bin) {
      const x = left ? this.xScale(bin.length) : 0;
      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
          return x;
        }
        const binLen = this.populationCounts[bin.x0];
        return left ? this.xScale(binLen) : 0;
      }
      return x;
    },
    getNonCohortWidth(left, bin) {
      const barWidth = left
        ? this.w - this.xScale(bin.length) > 0
          ? this.w - this.xScale(bin.length)
          : 0
        : this.xScale(bin.length) > 0
        ? this.xScale(bin.length)
        : 0;

      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
          return barWidth;
        }
        const binLen = this.populationCounts[bin.x0];
        return left
          ? this.w - this.xScale(binLen) > 0
            ? this.w - this.xScale(binLen)
            : 0
          : this.xScale(binLen) > 0
          ? this.xScale(binLen)
          : 0;
      }
      return barWidth;
    },
    getOpacity(subset) {
      return 1;
    },
    resizeChart() {
      this.height = 300;
      this.width = 120;
    },
  },
};
</script>

<style scoped></style>
