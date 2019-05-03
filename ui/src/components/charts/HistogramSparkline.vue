<template>
  <div>
    <svg ref="histogram" :width="w" :height="h">
      <!-- <g :transform="`translate(${margin.left}, ${margin.top})`"> -->
      <g>
        <rect
          v-for="(bin, i) in bins"
          :key="i"
          :transform="`translate(${xScale(bin.x0)}, ${yScale(bin.length)})`"
          :width="xScale(bin.x1) - xScale(bin.x0) - 1"
          :height="height - yScale(bin.length)"
        />
        <!-- TODO: Key needs to be random to fix pagination bug on table... -->
      </g>
    </svg>
  </div>
</template>

<script>
import { histogram, extent, max } from 'd3-array';
import { scaleLinear } from 'd3-scale';
import { uniqueId } from 'lodash';

export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
    width: {
      type: Number,
      default: 100,
    },
    height: {
      type: Number,
      default: 25,
    },
    value: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isLoading: true,
      margin: {
        top: 2,
        right: 2,
        bottom: 2,
        left: 2,
      },
    };
  },
  computed: {
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
        .domain(extent(this.data, d => +d[this.value]))
        .range([0, this.w]);
    },
    binData() {
      return histogram()
        .value(d => d[this.value])
        .domain(this.xScale.domain());
    },
    bins() {
      return this.binData(this.data);
    },
    yScale() {
      return scaleLinear()
        .range([this.h, 0])
        .domain([0, max(this.bins, d => d.length)]);
    },
  },
  methods: {
    uniqueId,
  },
};
</script>

<style lang="scss" scoped></style>
