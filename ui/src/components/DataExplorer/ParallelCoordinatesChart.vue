<template>
  <v-flex ref="container" fill-height>
    <!-- Parallel Coordinates -->
    <canvas ref="canvas" :width="width" :height="height"> </canvas>
  </v-flex>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';
import { scalePoint, scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import { axisLeft, axisRight } from 'd3-axis';
import { max } from 'd3-array';

export default {
  directives: {
    dimension(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
    },
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
      devicePixelRatio: 1,
      width: 0,
      height: 0,
      margin: { top: 20, right: 25, bottom: 15, left: 25 },
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      filteredData: state.DATA,
      unfilteredData: state.DATA,
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
      return height - top - bottom;
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
  created() {
    this.devicePixelRatio = window.devicePixelRatio || 1;
  },
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
    resizeChart() {
      const { height } = this.container.getBoundingClientRect();
      this.height = height;
      this.width = 175;
      // this.context.scale(this.devicePixelRatio, this.devicePixelRatio);
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
    drawLeftAxis() {
      const tickCount = 10;
      const tickSize = 6;
      const tickPadding = 3;
      const ticks = this.dimensionScale.ticks(tickCount);
      const tickFormat = this.dimensionScale.tickFormat(tickCount);

      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(0, this.dimensionScale(d));
        this.context.lineTo(-6, this.dimensionScale(d));
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(-tickSize, 0);
      this.context.lineTo(0.5, 0);
      this.context.lineTo(0.5, this.computedHeight);
      this.context.lineTo(-tickSize, this.computedHeight);
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = 'right';
      this.context.textBaseline = 'middle';
      ticks.forEach(d => {
        this.context.fillText(
          tickFormat(d),
          -tickSize - tickPadding,
          this.dimensionScale(d)
        );
      });
      this.context.save();
    },
    drawRightAxis() {
      const tickCount = 10;
      const tickSize = 6;
      const tickPadding = 3;
      const ticks = this.dimensionScale.ticks(tickCount);
      const tickFormat = this.dimensionScale.tickFormat(tickCount);

      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(
          this.xDimensionScale('Last Visit'),
          this.dimensionScale(d)
        );
        this.context.lineTo(
          this.xDimensionScale('Last Visit') + 6,
          this.dimensionScale(d)
        );
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(this.xDimensionScale('Last Visit') + tickSize, 0);
      this.context.lineTo(this.xDimensionScale('Last Visit') + 0.5, 0);
      this.context.lineTo(
        this.xDimensionScale('Last Visit') + 0.5,
        this.computedHeight
      );
      this.context.lineTo(
        this.xDimensionScale('Last Visit') + tickSize,
        this.computedHeight
      );
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = 'left';
      this.context.textBaseline = 'middle';
      ticks.forEach(d => {
        this.context.fillText(
          tickFormat(d),
          this.xDimensionScale('Last Visit') + tickSize + tickPadding,
          this.dimensionScale(d)
        );
      });
      this.context.save();
    },
    drawAxes() {
      this.drawLeftAxis();
      this.drawRightAxis();
    },
    updateCanvas() {
      this.context.clearRect(0, 0, this.computedWidth, this.computedHeight);
      this.context.translate(this.margin.left, 0);
      // this.drawUnfiltered();
      this.drawFiltered();
      this.drawAxes();
    },
  },
};
</script>

<style lang="scss" scoped></style>
