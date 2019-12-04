<template>
  <v-flex ref="container" fill-height>
    <svg ref="chart" :width="width" :height="height">
      <g
        v-if="width && height"
        ref="bars"
        :transform="`translate(${margin.left}, ${margin.top})`"
      >
        <rect
          v-for="(bin, i) in bins"
          :key="i"
          :transform="`translate(${xScale(bin.x0)}, ${yScale(bin.length)})`"
          :width="xScale(bin.x1) - xScale(bin.x0) - 1"
          :height="h - yScale(bin.length)"
          fill="#33d8ff"
        />
      </g>
      <g
        v-xaxis="xAxis"
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
import { extent, max, histogram } from 'd3-array';
import { select } from 'd3-selection';
import { scaleLinear } from 'd3-scale';
import 'd3-transition';
import { axisBottom, axisLeft } from 'd3-axis';
// import { schemeCategory10 } from 'd3-scale-chromatic';
// Directives
import resize from 'vue-resize-directive';
// Components
// import BarRect from './BarRect.vue';

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
    },
    yaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
    },
  },
  components: {},
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
        .domain(extent(this.data))
        .range([0, this.w]);
    },
    bins() {
      return histogram()
        .domain(this.xScale.domain())
        .thresholds(this.xScale.ticks(30))(this.data);
    },
    yScale() {
      const yScale = scaleLinear()
        .domain([0, max(this.bins, d => d.length)])
        .range([this.h, 0]);
      return yScale;
    },
    xAxis() {
      return axisBottom(this.xScale);
    },
    yAxis() {
      return axisLeft(this.yScale).ticks(3);
    },
  },
  watch: {
    filteredData() {
      // this.data = flattenGroupCounts(this.group.all());
      // if (this.selected.length && !this.dimension.currentFilter()) {
      // this.selected = [];
      // }
    },
  },
  created() {
    const dimension = this.dimensions[this.dimensionName];
    this.dimension = dimension;
    this.data = this.unfilteredData.map(dimension.accessor);
  },
  mounted() {
    this.container = this.$refs.container;

    // Resize chart so we have parent dimensions (width/height)
    this.resizeChart();
  },
  methods: {
    ...mapActions('cohortManager', {
      addFilter: actions.ADD_FILTER,
      clearFilter: actions.CLEAR_FILTER,
    }),
    getFill(key) {
      if (!this.selected.length || this.selected.includes(key)) {
        return this.colorScale(key);
      }
      return '#E8EAF6';
    },
    userClickedBar(key) {
      if (this.selected.includes(key)) {
        this.selected = this.selected.filter(d => d !== key);
      } else {
        this.selected.push(key);
      }

      if (this.selected.length) {
        this.addFilter({
          dimension: this.dimensionName,
          filter: d => this.selected.includes(d),
        });
      } else {
        this.clearFilter({
          dimension: this.dimensionName,
        });
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

<style lang="scss" scoped></style>
