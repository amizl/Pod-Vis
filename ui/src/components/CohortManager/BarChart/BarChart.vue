<template>
  <v-flex ref="container" fill-height>
    <svg ref="chart" :width="width" :height="height">
      <g
        v-if="width && height"
        ref="bars"
        :transform="`translate(${margin.left}, ${margin.top})`"
      >
        <bar-rect
          v-for="d in populationData"
          :key="`population-${d.key}`"
          :x="xScale(d.key)"
          :y="yScale(d.value)"
          :width="xScale.bandwidth()"
          :height="h - yScale(d.value) > 0 ? h - yScale(d.value) : 0"
          fill="#E8EAF6"
          @click.native="userClickedBar(d.key)"
        />
        <bar-rect
          v-for="d in data"
          :key="`cohort-${d.key}`"
          :x="xScale(d.key)"
          :y="yScale(d.value)"
          :width="xScale.bandwidth()"
          :height="h - yScale(d.value) > 0 ? h - yScale(d.value) : 0"
          :fill="getFill(d.key)"
          @click.native="userClickedBar(d.key)"
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
import { max } from 'd3-array';
import { select } from 'd3-selection';
import { scaleLinear, scaleBand, scaleOrdinal } from 'd3-scale';
import 'd3-transition';
import { axisBottom, axisLeft } from 'd3-axis';
import { schemeCategory10 } from 'd3-scale-chromatic';
// Directives
import resize from 'vue-resize-directive';
// Components
import BarRect from './BarRect.vue';

export default {
  directives: {
    resize,
    xaxis(el, binding) {
      const axisMethod = binding.value;
      select(el).call(axisMethod);
      // .selectAll('path')
      // .attr('stroke', '#E8EAF6')
      // .attr('stroke-width', 3);
    },
    yaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
      // .selectAll('path')
      // .attr('stroke', '#E8EAF6')
      // .attr('stroke-width', 3);
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
    colorScale() {
      return scaleOrdinal()
        .domain(this.data.map(c => c.key))
        .range(schemeCategory10);
    },
    xScale() {
      return scaleBand()
        .domain(this.populationData.map(d => d.key))
        .range([0, this.w])
        .padding(0.05);
    },
    yScale() {
      return scaleLinear()
        .domain([0, max(this.populationData, d => d.value)])
        .range([this.h, 0]);
    },
    xAxis() {
      return axisBottom(this.xScale);
    },
    yAxis() {
      return axisLeft(this.yScale).ticks(5);
    },
  },
  watch: {
    filteredData() {
      this.data = this.group.all();

      if (this.selected.length && !this.dimension.currentFilter()) {
        this.selected = [];
      }
    },
  },
  created() {
    const dimension = this.dimensions[this.dimensionName];
    this.dimension = dimension;
    this.group = dimension.group();
    this.data = this.group.all();
    this.populationData = this.data.map(d => ({ ...d }));
  },
  mounted() {
    this.container = this.$refs.container;
    // this.bars = select(this.$refs.bars).selectAll('.bar');

    // Resize chart so we have parent dimensions (width/height)
    this.resizeChart();
    // this.drawBars();
  },
  methods: {
    ...mapActions('cohortManager', {
      addFilter: actions.ADD_FILTER,
      clearFilter: actions.CLEAR_FILTER,
    }),
    getFill(key) {
      if (!this.selected.length || this.selected.includes(key)) {
        // if (key == 'female') {
        //   return '#FFC0CB';
        // } else if (key == 'male') {
        //   return '#3498DB';
        // } else {
        //   return this.colorScale(key);
        // }
        return '#3F51B5';
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

<style lang="scss" scoped></style>
