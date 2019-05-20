<template>
  <div></div>
  <!-- <div>{{ id }} {{ label }}</div> -->
  <!-- <div>
    <svg ref="chart" :width="width" :height="height">
      <g :transform="`translate(${margin.left}, ${margin.top})`">
        <rect
          v-for="(d, i) in counts"
          :key="i"
          :x="xScale(d.key)"
          :y="yScale(d.value)"
          :width="xScale.bandwidth()"
          :height="h - yScale(d.value)"
          :fill="colorScale(d.key)"
          @click="console.log(d)"
        >
          <text :x="xScale(d.key)" :y="yScale(d.value)" fill="white">
            {{ d.value }}
          </text>
        </rect>

      </g>
      <g v-xaxis="xAxis" :transform="`translate(${margin.left},${h + 10})`"></g>
      <g
        v-yaxis="yAxis"
        :transform="`translate(${margin.left}, ${margin.top})`"
      ></g>
    </svg>
  </div> -->
</template>

<script>
import { max } from 'd3-array';
import { select } from 'd3-selection';
import { nest } from 'd3-collection';
import { scaleLinear, scaleBand, scaleOrdinal } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import { uniqBy } from 'lodash';
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';
import { schemeCategory10 } from 'd3-scale-chromatic';

export default {
  directives: {
    xaxis(el, binding) {
      const axisMethod = binding.value;
      select(el).call(axisMethod);
    },
    yaxis(el, binding) {
      const axisMethod = binding.value;
      select(el).call(axisMethod);
    },
  },
  props: {
    id: {
      type: Number,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    // data: {
    //   type: Array,
    //   required: true,
    // },
    width: {
      type: Number,
      default: 375,
    },
    height: {
      type: Number,
      default: 200,
    },
  },
  data() {
    return {
      isLoading: true,
      margin: {
        top: 10,
        right: 30,
        bottom: 20,
        left: 30,
        counts: [],
      },
    };
  },
  computed: {
    ...mapState('cohortManager', {
      data: state.DATA,
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
        .domain(this.counts.map(c => c.key))
        .range(schemeCategory10);
    },
    xScale() {
      return scaleBand()
        .domain(this.counts.map(d => d.key))
        .range([0, this.w])
        .padding(0.05);
    },
    yScale() {
      return scaleLinear()
        .domain([0, max(this.counts, d => d.value)])
        .range([this.h, 0]);
    },
    xAxis() {
      return axisBottom(this.xScale);
    },
    yAxis() {
      return axisLeft(this.yScale);
    },
  },
  created() {
    const subjects = uniqBy(this.data, e => e.subject_id).map(subject => {
      return {
        [this.label]: subject[this.label],
      };
    });

    const counts = nest()
      .key(d => d[this.label])
      .rollup(v => v.length)
      .entries(subjects);

    this.counts = counts;
  },
  mounted() {},
  // mounted() {
  //   select(this.$refs.xScale).call(this.xAxis);
  //   select(this.$refs.yScale).call(this.yAxis);
  // },
  // methods: {
  //   uniqueId,
  // },
};
</script>

<style lang="scss" scoped></style>
