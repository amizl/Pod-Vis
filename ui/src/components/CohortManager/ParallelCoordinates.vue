<template>
  <v-flex ref="container" fill-height style="display: inline-block">
    <!-- First Visit histogram -->
    <VerticalHistogram
      :id="`firstVisit-${dimensionName}`"
      left
      :dimension-name="`${variable.label} - First Visit`"
      :y-domain="maxValueBetweenDimensions"
    />
    <!-- Parallel Coordinates -->
    <canvas ref="canvas" :width="computedWidth" :height="computedHeight" style='padding: 0px 0px 8px 0px; margin: 0px;'>
    </canvas>
    <!-- Last visit histogram -->
    <VerticalHistogram
      :id="`lastVisit-${dimensionName}`"
      :dimension-name="`${variable.label} - Last Visit`"
      :y-domain="maxValueBetweenDimensions"
    />

    <!-- PARACOORDS: SVG edition (slower since each line will live on the DOM) -->
    <!-- <svg ref="chart" :width="width" :height="height">
      <g ref="bars" :transform="`translate(${margin.left}, ${margin.top})`">
        <text
          fill="black"
          text-anchor="middle"
          y="-9"
          :x="xDimensionScale('First Visit')"
        >
          First Visit
        </text>
        <g
          v-dimension="firstVisitAxis"
          :transform="`translate(${xDimensionScale('First Visit')})`"
        ></g>
        <text
          fill="black"
          text-anchor="middle"
          y="-9"
          :x="xDimensionScale('Last Visit')"
        >
          Last Visit
        </text>
        <g
          v-dimension="lastVisitAxis"
          :transform="`translate(${xDimensionScale('Last Visit')})`"
        />
        <path
          v-for="(path, i) in populationPaths"
          :key="i"
          :d="path"
          stroke="#E8EAF6"
          opacity="1"
        />
        <path
          v-for="(path, i) in paths"
          :key="i"
          :d="path"
          stroke="#3F51B5"
          stroke-width="1"
          opacity=".45"
        />
      </g>
    </svg> -->
  </v-flex>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import { scalePoint, scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import { axisLeft, axisRight } from 'd3-axis';
import { max } from 'd3-array';
// import { line, curveMonotoneX } from 'd3-shape';
import VerticalHistogram from '@/components/CohortManager/VerticalHistogram/VerticalHistogram.vue';

export default {
  directives: {
    dimension(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
    },
  },
  components: {
    VerticalHistogram,
  },
  props: {
    dimensionName: {
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
      width: 0,
      height: 0,
      margin: { top: 20, right: 25, bottom: 10, left: 25 },
    };
  },
  computed: {
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      dimensions: state.DIMENSIONS,
    }),
    populationData() {
      return this.unfilteredData.map(d => d[this.dimensionName]);
    },
    cohortData() {
      return this.filteredData.map(d => d[this.dimensionName]);
    },
    populationPaths() {
      return this.populationData.map(d => {
        const firstVisitCoordinates = {
          x: this.xDimensionScale('First Visit'),
          y: this.dimensionScale(d.firstVisit),
        };
        const lastVisitCoordinates = {
          x: this.xDimensionScale('Last Visit'),
          y: this.dimensionScale(d.lastVisit),
        };
        return {
          firstVisitCoordinates,
          lastVisitCoordinates,
        };
      });
    },
    paths() {
      return this.cohortData.map(d => {
        const firstVisitCoordinates = {
          x: this.xDimensionScale('First Visit'),
          y: this.dimensionScale(d.firstVisit),
        };
        const lastVisitCoordinates = {
          x: this.xDimensionScale('Last Visit'),
          y: this.dimensionScale(d.lastVisit),
        };
        return {
          firstVisitCoordinates,
          lastVisitCoordinates,
        };
      });
    },

    maxValueBetweenDimensions() {
      const firstMax = max(this.populationData, d => d.firstVisit);
      const lastMax = max(this.populationData, d => d.lastVisit);
      return Math.max(firstMax, lastMax);
    },
    computedWidth() {
      const { left, right } = this.margin;
      const { width } = this;
      return width - left - right;
    },
    computedHeight() {
      const { top, bottom } = this.margin;
      const { height } = this;
      return height - top - bottom - 4;
    },
    xDimensionScale() {
      return scalePoint()
        .domain(['First Visit', 'Last Visit'])
        .range([0, this.computedWidth]);
    },
    dimensionScale() {
      const scale = scaleLinear()
        .domain([0, this.maxValueBetweenDimensions])
        .range([this.computedHeight, 0]);
      return scale;
    },
    firstVisitAxis() {
      return axisLeft()
        .scale(this.dimensionScale)
        .tickSize(0);
    },
    lastVisitAxis() {
      return axisRight()
        .scale(this.dimensionScale)
        .tickSize(0);
    },
  },
  watch: {
    cohortData() {
      this.updateCanvas();
    },
  },
  created() {},
  mounted() {
    this.container = this.$refs.container;
    this.canvas = this.$refs.canvas;
    this.context = select(this.canvas)
      .node()
      .getContext('2d');

    // Resize chart so we have parent dimensions (width/height)
    this.resizeChart();

    this.$nextTick(() => this.updateCanvas());
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
    }),
    resizeChart() {
      this.height = 300;
      this.width = 200;
    },
    drawCurve({ firstVisitCoordinates, lastVisitCoordinates }, color, alpha) {
      const { context } = this;
      context.lineWidth = 1;
      context.strokeStyle = color;
      context.globalAlpha = alpha;

      context.beginPath();
      context.moveTo(firstVisitCoordinates.x, firstVisitCoordinates.y);
      context.bezierCurveTo(
        firstVisitCoordinates.x +
          (lastVisitCoordinates.x - firstVisitCoordinates.x) / 4,
        firstVisitCoordinates.y,
        lastVisitCoordinates.x -
          (lastVisitCoordinates.x - firstVisitCoordinates.x) / 4,
        lastVisitCoordinates.y,
        lastVisitCoordinates.x,
        lastVisitCoordinates.y
      );
      context.stroke();
    },
    drawUnfiltered() {
      this.populationPaths.forEach(path => this.drawCurve(path, '#E8EAF6', 1));
    },
    drawFiltered() {
      this.paths.forEach(path => this.drawCurve(path, '#3F51B5', 0.45));
    },
    updateCanvas() {
      this.context.clearRect(0, 0, this.width, this.height);
      this.drawUnfiltered();
      this.drawFiltered();
    },
  },
};
</script>

<style lang="scss" scoped></style>
