<template>
  <v-flex ref="container" fill-height>
    <!-- Detailed View Chart -->
    <canvas ref="canvas" :width="width" :height="height"> </canvas>
  </v-flex>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/dataExplorer/types';
import { scalePoint, scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import { axisLeft, axisRight } from 'd3-axis';
import { max, mean, deviation } from 'd3-array';

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
    // not the dimension name, it's actually the dimension/database id
    dimensionName: {
      type: Number,
      required: true,
    },
    variable: {
      type: Object,
      required: true,
    },
    lineStyle: {
      type: String,
      required: true,
    },
    drawMean: {
      type: Boolean,
      required: true,
    },
    xaxis: {
      type: String,
      required: true,
    },

  },
  data() {
    return {
      devicePixelRatio: 1,
      width: 0,
      height: 0,
      margin: { top: 20, right: 25, bottom: 15, left: 25 },
//      draw_mean: false,
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      data: state.DATA,
      rawData: state.RAW_DATA,
      cohorts: state.COHORTS,
      visibleCohorts: state.VISIBLE_COHORTS,
      collection: state.COLLECTION,
    }),
    getRawData() {
      var filtered = this.rawData.filter(d => d.observation_ontology_id === this.dimensionName);

      // group by subject id      
      var subj2data = {};
      filtered.forEach(function(r) {
        if (!(r.subject_id in subj2data)) {
          subj2data[r.subject_id] = [];
        }
        subj2data[r.subject_id].push(r);
      });

      // compute subject-relative time in days
      Object.keys(subj2data).forEach(function(k) {
        var rows = subj2data[k];
        var srows = rows.sort((a, b) => a['event_day']-b['event_day']);
        var first_day = srows[0]['event_day'];
        var ind = 0;
        rows.forEach(function(r) {
          r['subject_event_day'] = r['event_day'] - first_day;
          r['subject_event_index'] = ind++;
          // TODO - subject_event_index may differ from visit_num
        });
      });

      return filtered;
    },
    yAxisRangeMax() {
      var rd = this.getRawData;
      const rmax = max(rd, d => d.total);
      return rmax;
    },

    // --------------------------------------------------
    // x-axis
    // --------------------------------------------------
    xaccessor() {
      if (this.xaxis === "days") {
        return function(x) { return x.subject_event_day; };
      } else {
        return function(x) { return x.subject_event_index; };
      }
    },
    timepoints() {
      var rd = this.getRawData;
      var timepoints = {};
      var xacc = this.xaccessor;
      rd.forEach(function(x) {
        timepoints[xacc(x)] = 1;
      });
      return Object.keys(timepoints).sort((a, b) => a-b);
    },
    xmin() {
      var tp = this.timepoints;
      return tp[0];
    },
    xmax() {
      var tp = this.timepoints;
      // TODO - allow user to adjust xmax up to the limit
      return tp[tp.length-1];
    },
    xDimensionScale() {
      return scaleLinear()
        .domain([0, this.xmax])
        .range([0, this.computedWidth]);
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
    dimensionScale() {
      const scale = scaleLinear()
        .domain([0, this.yAxisRangeMax])
        .range([this.computedHeight, 0]);
      return scale;
    },
  },
  watch: {
    rawData() {
      this.updateCanvas();
    },
    dimensionName() {
      this.updateCanvas();
    },
    lineStyle() {
      this.updateCanvas();
    },
    xaxis() {
      this.updateCanvas();
    },
    drawMean() {
      this.updateCanvas();
    },
    cohorts() {
      this.updateCanvas();
    },
    visibleCohorts() {
      this.updateCanvas();
    }
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

    this.$root.$on('update_detailed_view', () => {
      this.updateCanvas();
    });
  },
  methods: {

    selectedCohorts() {
      var cch = [];
      var cid = this.collection.id

      this.visibleCohorts.forEach(function(e) {
      if (e.collection_id === cid) {
          cch.push(e);
        }
      });

      return cch;
    },

    getRawPaths(subject_ids) {
      var rd = this.getRawData;
      var xds = this.xDimensionScale;
      var ds = this.dimensionScale;
      var xacc = this.xaccessor;

      // group raw data by subject id
      var subj2coords = {};
      rd.forEach(function(r) {
        if (!(r.subject_id in subj2coords)) {
          subj2coords[r.subject_id] = [];
        }
        subj2coords[r.subject_id].push({"x":xds(xacc(r)), "y":ds(r.total)});
      });

      // extract paths for each subject
      var paths = [];
      subject_ids.forEach(function(k) {
        var coords = subj2coords[k];
        if (coords !== undefined) {
          paths.push(coords);
        }
      });
      return paths;
    },

    getMeanAndSDPaths(subject_ids) {
      var rd = this.getRawData;
      var xds = this.xDimensionScale;
      var ds = this.dimensionScale;
      var xacc = this.xaccessor;
      var sjids = {};
      subject_ids.forEach(function(sid) {
        sjids[sid] = 1;
      });

      // group raw data by timepoint, filtering by subject_id
      var tp2data = {};
      rd.forEach(function(r) {
        if (!(r.subject_id in sjids)) {
          return;
        }
        var tp = xacc(r);
        if (!(tp in tp2data)) {
          tp2data[tp] = [];
        }
        tp2data[tp].push(r.total);
      });

      // extract paths for mean and mean +/- SD
      var mean_path = [];
      var mean_minus_sd_path = [];
      var mean_plus_sd_path = [];

      var sorted_tp = Object.keys(tp2data).sort((a, b) => a-b);

      sorted_tp.forEach(function(tp) {
        var data = tp2data[tp];
        var mn = mean(data);
        var sd = deviation(data);
        // TODO - determine whether this is the best approach - normally sd is undefined for a sample of size 1
        if (sd === undefined) {
          sd = 0;
        }
        var xp = xds(tp);
        mean_path.push({"x": xp, "y": ds(mn)});
        mean_minus_sd_path.push({"x": xp, "y": ds(mn - sd)});
        mean_plus_sd_path.push({"x": xp, "y": ds(mn + sd)});
      });

      return [mean_path, mean_minus_sd_path, mean_plus_sd_path];
    },

    resizeChart() {
      const { width, height } = this.container.getBoundingClientRect();
      this.height = height;
      // HACK
      this.width = 500;
      // this.context.scale(this.devicePixelRatio, this.devicePixelRatio);
    },

    traceMultiCurve(context, coords) {
      var lastCoords = undefined;

      // TODO - use clip rect to truncate curves/lines at right axis
      
      // bezier curves
      if (this.lineStyle === 'bezier') {
        coords.forEach(function(c) {
          if (lastCoords === undefined) {
            context.moveTo(coords[0].x, coords[0].y);
          } else {
            context.bezierCurveTo(
              lastCoords.x + (c.x - lastCoords.x) / 4, lastCoords.y,
              c.x - (c.x - lastCoords.x) / 4, c.y, c.x, c.y);
          }
          lastCoords = c;
        });
      } 
      // straight lines
      else {
        coords.forEach(function(c) {
          if (lastCoords === undefined) {
            context.moveTo(coords[0].x, coords[0].y);
          } else {
            context.lineTo(c.x, c.y);
          }
          lastCoords = c;
        });
      }
    },    

    drawMultiCurve(coords, color, alpha, lineWidth=1) {
      const { context } = this;
      var savedLineWidth = context.lineWidth
      context.lineWidth = lineWidth;
      context.strokeStyle = color;
      context.globalAlpha = alpha;

      context.beginPath();
      this.traceMultiCurve(context, coords);

      context.stroke();
      context.lineWidth = savedLineWidth;
    },

    drawMultiCurveRegion(coords1, coords2, strokeColor, fillColor, alpha, lineWidth=1) {
      const { context } = this;
      var savedLineWidth = context.lineWidth
      var savedFillColor = context.fillStyle
      var savedStrokeColor = context.strokeStyle

      context.lineWidth = lineWidth;
      context.strokeStyle = strokeColor;
      context.globalAlpha = alpha;
      context.fillStyle = fillColor;

      context.beginPath();

      this.traceMultiCurve(context, coords1);
      context.lineTo(coords2[coords2.length - 1].x, coords2[coords2.length - 1].y);
      this.traceMultiCurve(context, coords2.reverse());
      context.lineTo(coords1[0].x, coords1[0].y);

      context.fill();
      context.stroke();
      context.lineWidth = savedLineWidth;
      context.fillStyle = savedFillColor;
      context.strokeStyle = savedStrokeColor;
    },

    drawRaw() {
      var cohorts = this.selectedCohorts();
      var slf = this;

      const dimension2field = {
        "left_y_axis": "firstVisit",
        "right_y_axis": "lastVisit",
        "change": "change",
        "roc": "roc"
      };

      // draw each cohort in turn
      cohorts.forEach(function(c) {
        console.log("cohort " + c.label + " color = " + c.color);
        var cohort_subject_ids = c.subject_ids;

        // draw mean and standard deviation for entire group
        if (slf.drawMean) {
          var paths = slf.getMeanAndSDPaths(cohort_subject_ids);
          // +/- 1 SD
          slf.drawMultiCurveRegion(paths[1], paths[2], 'black', '#d0d0d0', 0.4, 0.5);
          // mean
          slf.drawMultiCurve(paths[0], c.color, 0.6, 8);
          // outline +/- 1 SD
          slf.drawMultiCurve(paths[1], c.color, 0.6, 1);
          slf.drawMultiCurve(paths[2], c.color, 0.6, 1);
        } else {
          // draw single path for each subject
          var paths = slf.getRawPaths(cohort_subject_ids);
          paths.forEach(path => slf.drawMultiCurve(path, c.color, 0.45));
        }
      });
    },
    drawLeftAxis() {
      var tickCount = 10,
        tickSize = 6,
        tickPadding = 3,
        ticks = this.dimensionScale.ticks(tickCount),
        tickFormat = this.dimensionScale.tickFormat(tickCount);

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
      var tickCount = 10,
        tickSize = 6,
        tickPadding = 3,
        ticks = this.dimensionScale.ticks(tickCount),
        tickFormat = this.dimensionScale.tickFormat(tickCount),
        xmax = this.xmax;

      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(
          this.xDimensionScale(xmax),
          this.dimensionScale(d)
        );
        this.context.lineTo(
          this.xDimensionScale(xmax) + tickSize,
          this.dimensionScale(d)
        );
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(this.xDimensionScale(xmax) + tickSize, 0);
      this.context.lineTo(this.xDimensionScale(xmax) + 0.5, 0);
      this.context.lineTo(
        this.xDimensionScale(xmax) + 0.5,
        this.computedHeight
      );
      this.context.lineTo(
        this.xDimensionScale(xmax) + tickSize,
        this.computedHeight
      );
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = 'left';
      this.context.textBaseline = 'middle';
      ticks.forEach(d => {
        this.context.fillText(
          tickFormat(d),
          this.xDimensionScale(xmax) + tickSize + tickPadding,
          this.dimensionScale(d)
        );
      });
      this.context.save();
    },
    drawBottomAxis() {
      var tickCount = 10,
        tickSize = 6,
        tickPadding = 3,
        tp = this.timepoints,
        xmax = this.xmax;

      if (this.xaxis === "visits") {
        tickCount = tp.length;
      }

      var scale = scaleLinear().domain([0, this.xmax]).range([0, this.computedWidth]);
      var ticks = scale.ticks(tickCount);
      var tickFormat = scale.tickFormat(tickCount);
      var ds = this.dimensionScale;

      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(
          scale(d),
          this.dimensionScale(0)
        );
        this.context.lineTo(
          scale(d),
          this.dimensionScale(0) + tickSize
        );
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(this.xDimensionScale(0), this.computedHeight);
      this.context.lineTo(this.xDimensionScale(xmax) + 0.5, this.computedHeight);
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = 'center';
      this.context.textBaseline = 'middle';
      ticks.forEach(d => {
        this.context.fillText(
          tickFormat(d),
          this.xDimensionScale(d),
          this.dimensionScale(0) + tickSize + (tickPadding * 2)
        );
      });

      let caption = "visit number";
      if (this.xaxis === "days" ) {
        caption = "time in days since first visit";
      }

      this.context.fillText(
        caption,
        this.xDimensionScale(xmax/2),
        this.dimensionScale(0) + ( tickSize + tickPadding) * 3
      );

      this.context.save();
    },
    drawAxes() {
      this.drawLeftAxis();
      this.drawRightAxis();
      this.drawBottomAxis();
    },
    updateCanvas() {
      // TODO - adding 50 is a workaround to account for the right-hand axis, which is outside of the computed area
      this.context.clearRect(0, 0, this.computedWidth + this.margin.left + 50, this.computedHeight + 50);
      this.context.translate(this.margin.left, 0);
      this.drawRaw();
      this.drawAxes();
      this.context.translate(-this.margin.left, 0);
    },
  },
};
</script>

<style lang="scss" scoped></style>
