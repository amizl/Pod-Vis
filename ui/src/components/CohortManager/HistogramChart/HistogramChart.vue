<template>
  <div>
    <div ref="container">
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
            :x="xScale(bin.x0)"
            :y="yScale(bin.length)"
            :width="
              xScale(bin.x1) - xScale(bin.x0) - 1 > 0
                ? xScale(bin.x1) - xScale(bin.x0) - 1
                : 0
            "
            :height="h - yScale(bin.length) > 0 ? h - yScale(bin.length) : 0"
            :fill="colors['population']"
            :opacity="getOpacity('population')"
          />
          <rect
            v-for="(bin, i) in popMinusBins"
            v-if="highlightedSubset === 'non-cohort'"
            :key="`pop-minus-cohort-${i}`"
            :x="xScale(bin.x0)"
            :y="getNonCohortY(bin)"
            :width="
              xScale(bin.x1) - xScale(bin.x0) - 1 > 0
                ? xScale(bin.x1) - xScale(bin.x0) - 1
                : 0
            "
            :height="getNonCohortHeight(bin)"
            :fill="colors['nonCohort']"
            :opacity="getOpacity('non-cohort')"
          />
          <rect
            v-for="(bin, i) in bins"
            v-if="highlightedSubset === 'cohort'"
            :key="`cohort-${i}`"
            :x="xScale(bin.x0)"
            :y="getCohortY(bin)"
            :width="
              xScale(bin.x1) - xScale(bin.x0) - 1 > 0
                ? xScale(bin.x1) - xScale(bin.x0) - 1
                : 0
            "
            :height="getCohortHeight(bin)"
            :fill="colors['cohort']"
            :opacity="getOpacity('cohort')"
          />
          <!-- Cohort Mean -->
          <circle
            v-if="typeof mean !== 'undefined'"
            r="7"
            :cx="mean"
            :cy="h"
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
            :cx="populationMean"
            :cy="h"
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
          :transform="`translate(${margin.left},${h + margin.top})`"
        ></g>
        <g
          v-yaxis="yAxis"
          :transform="`translate(${margin.left}, ${margin.top})`"
        ></g>
      </svg>
    </div>

    <v-container v-if="inputVariable" fill-width class="pa-0 mx-3">
      <v-row class="pa-0 ma-0" justify="start" align="center">
        <v-col cols="5" class="center-text pa-0 ma-0"
          >Custom&nbsp;Selection:</v-col
        >
        <v-col cols="2" class="pa-0 ma-0" justify="start">
          <v-text-field
            v-model.number="tfRangeMin"
            :error-messages="rangeMinErrors"
            class="center-text pa-0 ma-0"
            type="number"
            @change="userChangedVariable"
          ></v-text-field
        ></v-col>
        <v-col cols="1" class="pa-0 ma-0" align="center" justify="center">
          -
        </v-col>
        <v-col cols="2" class="pa-0 ma-0">
          <v-text-field
            v-model.number="tfRangeMax"
            :error-messages="rangeMaxErrors"
            class="center-text pa-0 ma-0"
            type="number"
            @change="userChangedVariable"
          ></v-text-field>
        </v-col>
      </v-row>

      <v-row class="pa-0 ma-0">
        <v-col cols="12" class="pa-0 ma-0">
          <v-checkbox v-model="snapToGrid" label="Select whole bars only">
          </v-checkbox>
        </v-col>
      </v-row>

      <v-row class="pa-0 ma-0">
        <v-col cols="10" class="pa-0 ma-0">
          <v-select
            v-model="selectedPopSubset"
            :items="popSubsetItems"
            item-text="label"
            item-value="id"
            label="Pre-Programmed Selections"
            class="pa-0 ma-0"
            return-object
          ></v-select>
        </v-col>
      </v-row>

      <v-row class="pa-0 ma-0">
        <v-col cols="12" class="pa-0 ma-0">
          <create-comparator-cohorts-btn-dialog
            :dimension-name="variable.abbreviation"
            :select-cohort-range="selectCohortRange"
            :reset-selection="resetSelection"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
// Data Store
import { mapState, mapActions, mapGetters } from 'vuex';
import { state, getters, actions } from '@/store/modules/cohortManager/types';
// D3 Modules
import { extent, max, mean, histogram } from 'd3-array';
import { brushX, brushSelection } from 'd3-brush';
import { format } from 'd3-format';
import { select, event } from 'd3-selection';
import { scaleLinear } from 'd3-scale';
import 'd3-transition';
import { axisBottom, axisLeft } from 'd3-axis';
// Directives
import resize from 'vue-resize-directive';
// Components
import { colors } from '@/utils/colors';
import CreateComparatorCohortsBtnDialog from '@/components/CohortManager/CreateComparatorCohortsBtnDialog';

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
    CreateComparatorCohortsBtnDialog,
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
    variable: {
      type: Object,
      required: false,
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
      container: null,
      dimension: null,
      group: [],
      data: [],
      populationData: [],
      selection: [],
      populationCounts: {},
      colors: colors,
      selectedRange: null,
      selectedPopSubset: null,
      tfRangeMin: null,
      tfRangeMax: null,
      snapToGrid: true,
    };
  },
  computed: {
    ...mapGetters('cohortManager', {
      getQuery: getters.GET_QUERY,
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
    rangeMinErrors() {
      if (this.tfRangeMin) {
        if (this.tfRangeMin < this.min_value) {
          return ['Minimum is ' + this.min_value];
        }
        if (this.tfRangeMin > this.max_value) {
          return ['Maximum is ' + this.max_value];
        }
        if (this.tfRangeMax && this.tfRangeMin > this.tfRangeMax) {
          return ['Minimum is greater than maximum'];
        }
      }
      return [];
    },
    rangeMaxErrors() {
      if (this.tfRangeMax) {
        if (this.tfRangeMax < this.min_value) {
          return ['Minimum is ' + this.min_value];
        }
        if (this.tfRangeMax > this.max_value) {
          return ['Maximum is ' + this.max_value];
        }
        if (this.tfRangeMin && this.tfRangeMin > this.tfRangeMax) {
          return ['Maximum is less than minimum'];
        }
      }
      return [];
    },
    num_bins() {
      var ext = extent(this.populationData);
      var diff = ext[1] - ext[0];
      if (
        this.variable &&
        this.variable.value_type === 'decimal' &&
        diff < 30
      ) {
        return diff + 1;
      } else {
        return 30;
      }
    },
    min_value() {
      var ext = extent(this.populationData);
      var range = ext[1] - ext[0];
      // round to nearest int
      if (range >= 10) {
        return Math.floor(ext[0]);
      } else {
        return ext[0] - 0.5;
      }
    },
    // padded maximum value
    max_value() {
      var ext = extent(this.populationData);
      var range = ext[1] - ext[0];
      // round up to nearest int
      if (range >= 10) {
        return Math.ceil(ext[1] + 0.5);
      } else {
        return ext[1] + 0.5;
      }
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
        .thresholds(this.xScale.ticks(this.num_bins));
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
      // TODO - factor out code in common with VerticalHistogram.vue
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
    mean() {
      return this.xScale(mean(this.filteredData.map(this.dimension.accessor)));
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
    popSubsetItems() {
      var items = [];
      let ext = extent(this.populationData);
      let popData = this.populationData.slice().sort((a, b) => a - b);
      let pdl = popData.length;

      let median = this.getGenMedian(popData, 1, 2);
      let qtr1 = this.getGenMedian(popData, 1, 4);
      let qtr3 = this.getGenMedian(popData, 3, 4);
      let thr1 = this.getGenMedian(popData, 1, 3);
      let thr2 = this.getGenMedian(popData, 2, 3);
      let lower = this.min_value;
      let upper = this.max_value;

      items.push({ label: 'top 1/2', min: median, max: upper });
      items.push({ label: 'bottom 1/2', min: lower, max: median });

      items.push({ label: 'top 1/3', min: thr2, max: upper });
      items.push({ label: 'middle 1/3', min: thr1, max: thr2 });
      items.push({ label: 'bottom 1/3', min: lower, max: thr1 });

      items.push({ label: 'top 1/4', min: qtr3, max: upper });
      items.push({ label: 'bottom 3/4', min: lower, max: qtr3 });
      items.push({ label: 'bottom 1/4', min: lower, max: qtr1 });
      items.push({ label: 'top 3/4', min: qtr1, max: upper });
      items.forEach(i => {
        i.label = i.label + ' of population [' + i.min + ' - ' + i.max + ']';
      });

      return items;
    },
    rangeItems() {
      var items = [];
      let ext = extent(this.populationData);
      let mid = (ext[0] + ext[1]) / 2.0;
      let qtr = (ext[1] - ext[0]) / 4.0;
      let qtr1 = ext[0] + qtr;
      let qtr3 = ext[1] - qtr;
      let one_third = (ext[1] - ext[0]) / 3.0;
      let thr1 = Math.round(ext[0] + one_third);
      let thr2 = Math.round(ext[1] - one_third);
      let upper = this.max_value;

      items.push({ label: 'top 1/2', min: mid, max: upper });
      items.push({ label: 'bottom 1/2', min: ext[0], max: mid });

      items.push({ label: 'top 1/3', min: thr2, max: upper });
      items.push({ label: 'middle 1/3', min: thr1, max: thr2 });
      items.push({ label: 'bottom 1/3', min: ext[0], max: thr1 });

      items.push({ label: 'top 1/4', min: qtr3, max: upper });
      items.push({ label: 'bottom 3/4', min: ext[0], max: qtr3 });
      items.push({ label: 'bottom 1/4', min: ext[0], max: qtr1 });
      items.push({ label: 'top 3/4', min: qtr1, max: upper });
      items.forEach(i => {
        i.label = i.label + ' of range [' + i.min + '-' + i.max + ']';
      });

      return items;
    },
  },
  watch: {
    filteredData() {
      this.data = flattenGroupCounts(this.group.all());
      this.updateRangeFromQuery();
    },
    selectedRange(s) {
      if (s == null) {
        return;
      }
      this.selectedPopSubset = null;
      this.selectRange(s);
    },
    selectedPopSubset(s) {
      if (s == null) {
        return;
      }
      this.selectedRange = null;
      this.selectRange(s);
      this.$emit('userChangedVariable', this.dimension);
    },
    tfRangeMin(range_min) {
      this.updateSelectedRange();
    },
    tfRangeMax(range_max) {
      this.updateSelectedRange();
    },
    cohort(new_cohort) {
      this.updateRangeFromCohortQuery();
    },
  },
  created() {
    const dimension = this.dimensions[this.dimensionName];
    this.dimension = dimension;
    this.populationData = this.unfilteredData.map(dimension.accessor);
    this.group = dimension.group();
    this.data = flattenGroupCounts(this.group.all());
    this.updateRangeFromCohortQuery();
    this.updateRangeFromQuery();
  },
  destroyed() {
    this.resetSelection();
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
        const y = this.h / 2;
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
      const [low, high] = selection.map(this.xScale.invert);
      if (!this.snapToGrid) {
        return [low, high].map(this.xScale);
      }

      // Get closest bin to our lower selection
      const closestBinToLow = this.bins
        .map(bin => bin.x0)
        .map(x0 => Math.abs(x0 - low))
        .reduce((acc, currVal) => Math.min(acc, currVal));
      var newLowIdx = this.bins.findIndex(
        bin => Math.abs(bin.x0 - low) === closestBinToLow
      );
      const newLow = this.bins[newLowIdx].x0;
      // Get closest bin to our higher selection
      const closestBinToHigh = this.bins
        .map(bin => bin.x1)
        .map(x1 => Math.abs(x1 - high))
        .reduce((acc, currVal) => Math.min(acc, currVal));
      var newHighIdx = this.bins.findIndex(
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
        this.resetSelection();
        this.selectedRange = null;
        this.selectedPopSubset = null;
        this.$emit('userChangedVariable', this.dimension);
        return;
      }

      // Snap selections to closest bins
      const [low, high] = this.getClosestBins();

      select(this.$refs.brush)
        .transition()
        .call(event.target.move, [low, high]);

      var [invertedLow, invertedHigh] = [low, high].map(this.xScale.invert);
      this.selectedRange = null;
      this.selectedPopSubset = null;

      var fmt = format('.2~f');

      // workaround for when entire range is selected
      var last_bin = this.bins[this.bins.length - 1];
      if (last_bin.x0 == last_bin.x1) {
        last_bin = this.bins[this.bins.length - 2];
      }
      if (invertedHigh >= this.max_value) {
        invertedHigh = this.max_value;
      }

      invertedLow = fmt(invertedLow);
      invertedHigh = fmt(invertedHigh);

      // Filter dimension to be within snapped selection
      this.addFilter({
        dimension: this.dimensionName,
        filter: d => d >= invertedLow && d < invertedHigh,
        query: {
          minValue: invertedLow,
          maxValue: invertedHigh,
        },
      });
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
      this.handle
        .attr('display', null)
        .attr(
          'transform',
          (d, i) => `translate(${selection[i]},${-this.h / 4})`
        );

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
      const [low, high] = this.selection.map(this.xScale.invert);
      const { x0, x1 } = bin;

      // padding must be adaptive - set to half the bin width/height
      const PADDING = (x1 - x0) / 2.0;
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
      const y = this.yScale(bin.length);
      if (this.hasSelection()) {
        return this.isBinSelected(bin) ? y : this.yScale(0);
      }
      return y;
    },
    getCohortHeight(bin) {
      if (this.isBinSelected(bin)) {
        //      console.log("getCohortHeight() binx0=" + bin.x0 + " selected=" + this.isBinSelected(bin));
      }
      const barHeight =
        this.h - this.yScale(bin.length) > 0
          ? this.h - this.yScale(bin.length)
          : 0;
      if (this.hasSelection()) {
        return this.isBinSelected(bin) ? barHeight : 0;
      }
      return barHeight;
    },
    getNonCohortY(bin) {
      const y = this.yScale(bin.length);
      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
          return y;
        }
        const binLen = this.populationCounts[bin.x0];
        return this.yScale(binLen);
      }
      return y;
    },
    getNonCohortHeight(bin) {
      const barHeight =
        this.h - this.yScale(bin.length) > 0
          ? this.h - this.yScale(bin.length)
          : 0;
      if (this.hasSelection()) {
        if (this.isBinSelected(bin)) {
          return barHeight;
        }
        const binLen = this.populationCounts[bin.x0];
        return this.h - this.yScale(binLen) > 0
          ? this.h - this.yScale(binLen)
          : 0;
      }
      return barHeight;
    },
    getOpacity(subset) {
      return 1;
    },
    resizeChart() {
      this.height = 100;
      this.width = 350;
    },

    // generalized median n = numerator, d = denominator e.g. 2/3 n=2, d=3
    getGenMedian(data, n, d) {
      let len = data.length;
      let pivot = (len / d) * n;
      let pm = pivot - 0.5;
      let pp = pivot + 0.5;
      let pmi = Math.floor(pm);
      let ppi = Math.floor(pp);
      let pp_frac = pp - ppi;
      let pm_frac = 1.0 - pp_frac;
      return parseFloat(data[pmi] * pm_frac + data[ppi] * pp_frac).toFixed(1);
    },

    selectRange(s) {
      let minValue = s.min;
      let maxValue = s.max;
      this.addFilter({
        dimension: this.dimensionName,
        filter: d => d >= minValue && d < maxValue,
        query: {
          minValue,
          maxValue,
        },
      });
    },
    getCohortRangeEndpoint(ep, ext, data) {
      if (ep == 'min') {
        return ext[0];
      } else if (ep == 'max') {
        return this.max_value;
      } else {
        return this.getGenMedian(data, ep[0], ep[1]);
      }
    },
    // called by CreateComparatorCohortsBtnDialog
    resetSelection() {
      this.clearFilter({
        dimension: this.dimensionName,
      });
    },
    selectCohortRange(ss, t) {
      var data = null;
      // population
      if (t.startsWith('study population')) {
        data = this.populationData;
      }
      // cohort
      else {
        data = this.data;
      }
      let ext = extent(data);
      let sorted_d = data.slice().sort((a, b) => a - b);
      var min = this.getCohortRangeEndpoint(ss.min, ext, sorted_d);
      var max = this.getCohortRangeEndpoint(ss.max, ext, sorted_d);
      this.selectRange({ min, max });
    },
    updateRangeFromCohortQuery() {
      const [query] = this.findCohortQuery(this.dimensionName);
      if (typeof query !== 'undefined') {
        this.$nextTick(() => {
          const minValue = query.min_value;
          const maxValue = query.max_value;
          // Filter dimension to be within selection
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
    },
    updateRangeFromQuery() {
      // there should only be one query for a histogram...
      const query = this.getQuery(this.dimensionName);

      if (query == null || typeof query == 'undefined') {
        if (this.handle != null) {
          this.handle.attr('display', 'none');
          select(this.$refs.brush).call(this.brush.move, null);
        }
        this.selectedRange = null;
        this.selectedPopSubset = null;
        this.tfRangeMin = null;
        this.tfRangeMax = null;
      } else {
        this.$nextTick(() => {
          const minValue = query[0].minValue;
          const maxValue = query[0].maxValue;

          select(this.$refs.brush).call(this.brush.move, [
            this.xScale(minValue),
            this.xScale(maxValue),
          ]);

          if (this.tfRangeMin != query[0].minValue) {
            this.tfRangeMin = Number(query[0].minValue);
          }
          if (this.tfRangeMax != query[0].maxValue) {
            this.tfRangeMax = Number(query[0].maxValue);
          }
        });
      }
    },

    // update selected range based on tfRangeMin - tfRangeMax, if feasible
    updateSelectedRange() {
      if (this.tfRangeMin == null || this.tfRangeMax == null) {
        return;
      }
      var tfMin = Number(this.tfRangeMin);
      var tfMax = Number(this.tfRangeMax);

      if (tfMax > this.max_value) {
        return;
      }
      if (tfMin < this.min_value) {
        return;
      }

      // is this range already selected?
      var alreadySelected = true;

      if (select(this.$refs.brush) == null) {
        alreadySelected = false;
      } else {
        var bsel = brushSelection(this.$refs.brush);
        if (bsel == null) {
          alreadySelected = false;
        } else {
          var rangeMin = this.xScale.invert(bsel[0]);
          var rangeMax = this.xScale.invert(bsel[1]);
          if (tfMin < tfMax && (rangeMin != tfMin || rangeMax != tfMax)) {
            alreadySelected = false;
          }
        }
      }

      if (!alreadySelected) {
        var tfrmin = tfMin;
        var tfrmax = tfMax;

        select(this.$refs.brush).call(this.brush.move, [
          this.xScale(tfrmin),
          this.xScale(tfrmax),
        ]);

        this.addFilter({
          dimension: this.dimensionName,
          filter: d => d >= tfrmin && d < tfrmax,
          query: {
            minValue: tfrmin,
            maxValue: tfrmax,
          },
        });
      }
    },
  },
};
</script>

<style scoped>
.center-text >>> input {
  text-align: center;
}
</style>
