<template>
  <v-flex ref="container" fill-height>
    <svg ref="chart" :width="width" :height="height">
      <g ref="bars" :transform="`translate(${margin.left}, ${margin.top})`">
        <rect
          v-for="(bin, i) in bins"
          :key="i"
          :transform="`translate(${xScale(bin.x0)}, ${yScale(bin.length)})`"
          :width="xScale(bin.x1) - xScale(bin.x0) - 1"
          :height="h - yScale(bin.length)"
          fill="#3F51B5"
        />

        <!-- Cohort Mean -->
        <circle
          r="5"
          :cx="mean"
          :cy="h"
          fill="#ffa632"
          stroke="#ffa632"
          stroke-width="2"
          fill-opacity=".5"
        />
        <!-- Population Mean -->
        <circle
          r="5"
          :cx="populationMean"
          :cy="h"
          fill="#33d8ff"
          stroke="#33d8ff"
          stroke-width="2"
          fill-opacity=".5"
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
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
// D3 Modules
import { extent, max, mean, histogram } from 'd3-array';
import { brushX } from 'd3-brush';
import { select, event } from 'd3-selection';
import { arc } from 'd3-shape';
import { scaleLinear } from 'd3-scale';
import 'd3-transition';
import { axisBottom, axisLeft } from 'd3-axis';
import { debounce } from 'lodash';
// import { schemeCategory10 } from 'd3-scale-chromatic';
// Directives
import resize from 'vue-resize-directive';
// Components
import BarRect from '../BarChart/BarRect.vue';

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
  components: {
    BarRect,
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
    bins() {
      return histogram()
        .domain(this.xScale.domain())
        .thresholds(this.xScale.ticks(30))(this.data);
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
        .domain([0, max(this.bins, d => d.length)])
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
    // Similar to winnow.js
    // const [maxRecord] = dimension.top(1);
    // const maxValue = maxRecord[this.id].roc;
    // const [minRecord] = dimension.bottom(1);
    // const minValue = minRecord[this.id].roc;
    // const binWidth = (maxValue - minValue) / 30;
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
        .attr('fill', '#9FA8DA');

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
    brushedData() {
      const selection = event.selection;
      if (selection) {
        const [low, high] = selection.map(this.xScale.invert);
        this.addFilter({
          dimension: this.dimensionName,
          filter: d => d >= low && d < high,
        });
      } else {
        this.clearFilter({
          dimension: this.dimensionName,
        });
      }
    },
    brushed() {
      const selection = event.selection;
      if (selection) {
        // const [low, high] = selection.map(this.xScale.invert);
        this.handle.attr('display', null).attr('transform', (d, i) => {
          return 'translate(' + selection[i] + ',' + -this.h / 4 + ')';
        });
        // this.addFilter({
        //   dimension: this.dimensionName,
        //   filter: d => d >= low && d < high,
        // });
      } else {
        this.handle.attr('display', 'none');
        // this.clearFilter({
        //   dimension: this.dimensionName,
        // });
      }
    },
    getFill(key) {
      if (!this.selected.length || this.selected.includes(key)) {
        return this.colorScale(key);
      } else {
        return '#E8EAF6';
      }
    },
    userClickedBar(key) {
      if (this.selected.includes(key)) {
        this.selected = this.selected.filter(d => d != key);
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
    updateBars() {
      this.bars
        .data(this.data, d => d.key)
        .enter()
        .style('cursor', 'pointer')
        .on('click', d => this.userClickedBar(d.key))
        .attr('x', d => this.xScale(d.key))
        .attr('width', () => this.xScale.bandwidth())
        .attr('fill', d => this.getFill(d.key))
        .transition()
        .duration(1000)
        .attr('y', d => this.yScale(d.value))
        .attr('height', d =>
          this.h - this.yScale(d.value) > 0 ? this.h - this.yScale(d.value) : 0
        );
    },
    drawBars() {
      this.bars
        .data(this.data, d => d.key)
        .enter()
        .append('rect')
        .style('cursor', 'pointer')
        .on('click', d => this.userClickedBar(d.key))
        .attr('x', d => this.xScale(d.key))
        .attr('y', () => this.yScale(0))
        .attr('width', () => this.xScale.bandwidth())
        .attr('height', 0)
        .attr('fill', d => this.getFill(d.key))
        .transition()
        .duration(1000)
        .attr('y', d => this.yScale(d.value))
        .attr('height', d =>
          this.h - this.yScale(d.value) > 0 ? this.h - this.yScale(d.value) : 0
        );
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
