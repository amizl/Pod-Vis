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
    <canvas
      ref="canvas"
      :width="computedWidth"
      :height="computedHeight"
      style="padding: 0px 0px 8px 0px; margin: 0px;"
    >
    </canvas>
    <!-- Last visit histogram -->
    <VerticalHistogram
      :id="`lastVisit-${dimensionName}`"
      :dimension-name="`${variable.label} - Last Visit`"
      :y-domain="maxValueBetweenDimensions"
    />
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
import { colors } from '@/utils/colors';
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
      highlightedSubset: state.HIGHLIGHTED_SUBSET,
      dimensions: state.DIMENSIONS,
    }),
    populationData() {
      return this.unfilteredData.map(d => d[this.dimensionName]);
    },
    cohortData() {
      return this.filteredData.map(d => d[this.dimensionName]);
    },
    nonCohortData() {
      var cohortSubIds = {};
      this.filteredData.forEach(d => {
        cohortSubIds[d['subject_id']] = 1;
      });
      var nonCohortData = [];
      this.unfilteredData.forEach(d => {
        if (!(d['subject_id'] in cohortSubIds)) {
          nonCohortData.push(d);
        }
      });
      return nonCohortData.map(d => d[this.dimensionName]);
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
    cohortPaths() {
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
    nonCohortPaths() {
      return this.nonCohortData.map(d => {
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
    highlightedSubset() {
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
      this.populationPaths.forEach(path =>
        this.drawCurve(path, colors['population'], 1)
      );
    },
    drawFiltered() {
      if (this.highlightedSubset === 'cohort') {
        this.cohortPaths.forEach(path =>
          this.drawCurve(path, colors['cohort'], 0.45)
        );
      } else {
        this.nonCohortPaths.forEach(path =>
          this.drawCurve(path, colors['nonCohort'], 0.45)
        );
      }
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
