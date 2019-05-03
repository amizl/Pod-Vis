<template>
  <div>
    <svg ref="histogram" :width="w" :height="h">
      <!-- <g :transform="`translate(${margin.left}, ${margin.top})`"> -->
      <g>
        <rect
          v-for="(d, i) in data"
          :key="i"
          :x="xScale(d.value)"
          :y="yScale(d.count)"
          :width="xScale.bandwidth()"
          :height="h - yScale(d.count)"
        />
        <!-- TODO: Key needs to be random to fix pagination bug on table... -->
      </g>
    </svg>
  </div>
</template>

<script>
import { max } from 'd3-array';
// import { nest } from 'd3-collection';
import { scaleLinear, scaleBand } from 'd3-scale';
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
      return scaleBand()
        .domain(this.data.map(d => d.value))
        .range([0, this.w])
        .padding(0.05);
    },
    yScale() {
      return scaleLinear()
        .domain([0, max(this.data, d => d.count)])
        .range([this.h, 0]);
    },
  },
  methods: {
    uniqueId,
  },
};
</script>

<style lang="scss" scoped></style>
