<template>
  <v-container fluid fill-height class="ma-0 pa-0" style="max-width: 425px;">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <div style="width: 280px; float: left;">
          Visit: {{ firstVisitLabel }}
        </div>
        <div>
          <p class="text-left">Visit: {{ lastVisitLabel }}</p>
        </div>
      </v-col>
    </v-row>

    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <!-- First Visit histogram -->
        <VerticalHistogram
          :id="`firstVisit-${dimensionName}`"
          left
          :dimension-name="`${variable.label} - First Visit`"
          :y-min="minValueBetweenDimensions"
          :y-domain="maxValueBetweenDimensions"
          :variable="variable"
          @userChangedVariable="userChangedVariable"
        />

        <!-- Parallel Coordinates -->
        <canvas
          ref="canvas"
          :width="computedWidth"
          :height="computedHeight"
          :style="'padding: 0px; margin: 0px;'"
        >
        </canvas>

        <!-- Last visit histogram -->
        <VerticalHistogram
          :id="`lastVisit-${dimensionName}`"
          :dimension-name="`${variable.label} - Last Visit`"
          :y-min="minValueBetweenDimensions"
          :y-domain="maxValueBetweenDimensions"
          :variable="variable"
          @userChangedVariable="userChangedVariable"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import { scalePoint, scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import { min, max } from 'd3-array';
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
    firstVisitLabel: {
      type: String,
      required: false,
      default: 'First Visit',
    },
    lastVisitLabel: {
      type: String,
      required: false,
      default: 'Last Visit',
    },
  },
  data() {
    return {
      width: 0,
      height: 0,
      margin: { top: 20, right: 0, bottom: 10, left: 0 },
      mounted: false,
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
    minValueBetweenDimensions() {
      const firstMin = min(this.populationData, d => d.firstVisit);
      const lastMin = min(this.populationData, d => d.lastVisit);
      return Math.min(firstMin, lastMin);
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
      const { height } = this;
      return height;
    },
    dimensionScale() {
      const scale = scaleLinear()
        .domain(
          this.variable.flip_axis
            ? [this.minValueBetweenDimensions, this.maxValueBetweenDimensions]
            : [this.maxValueBetweenDimensions, this.minValueBetweenDimensions]
        )
        .range([this.margin.top, this.computedHeight - this.margin.bottom]);
      return scale;
    },
  },
  watch: {
    cohortData() {
      this.$nextTick(() => this.updateCanvas());
    },
    highlightedSubset() {
      this.$nextTick(() => this.updateCanvas());
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
    this.mounted = true;

    this.$nextTick(() => this.updateCanvas());
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
    }),
    userChangedVariable() {
      this.$emit('userChangedVariable');
    },
    resizeChart() {
      this.height = 300;
      this.width = 140;
    },
    xDimensionScale(visit) {
      return visit == 'First Visit' ? 0 : this.computedWidth;
    },
    drawCurve({ firstVisitCoordinates, lastVisitCoordinates }) {
      const { context } = this;
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
      const { context } = this;
      context.lineWidth = 1;
      context.strokeStyle = colors['population'];
      context.globalAlpha = 1;
      this.populationPaths.forEach(path => this.drawCurve(path));
    },
    drawFiltered() {
      const { context } = this;
      context.lineWidth = 1;
      context.globalAlpha = 0.45;

      if (this.highlightedSubset === 'cohort') {
        context.strokeStyle = colors['cohort'];
        this.cohortPaths.forEach(path => this.drawCurve(path));
      } else {
        context.strokeStyle = colors['nonCohort'];
        this.nonCohortPaths.forEach(path => this.drawCurve(path));
      }
    },
    updateCanvas() {
      if (!this.mounted) return;
      this.context.clearRect(0, 0, this.width, this.height);
      this.drawUnfiltered();
      this.drawFiltered();
    },
  },
};
</script>

<style lang="scss" scoped></style>
