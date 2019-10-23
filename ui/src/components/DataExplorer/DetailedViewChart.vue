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
import { max } from 'd3-array';
import * as crossfilter from 'crossfilter2';

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
      data: state.DATA,
      rawData: state.RAW_DATA,
      lineStyle: state.LINE_STYLE,
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
        });
      });

      return filtered;
    },
    yAxisRangeMax() {
      var rd = this.getRawData;
      const rmax = max(rd, d => d.total);
      return rmax;
    },
    timepoints() {
      var rd = this.getRawData;
      var timepoints = {};
      rd.forEach(function(x) {
	  timepoints[x.subject_event_day] = 1;
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
      return scaleLinear()
        .domain([0, this.xmax])
        .range([0, this.computedWidth]);
    },
    dimensionScale() {
      const scale = scaleLinear()
        .domain([0, this.yAxisRangeMax])
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
    rawData() {
      this.updateCanvas();
    },
    dimensionName() {
      this.updateCanvas();
    },
    lineStyle() {
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

      // group raw data by subject id
      var subj2coords = {};
      rd.forEach(function(r) {
        if (!(r.subject_id in subj2coords)) {
          subj2coords[r.subject_id] = [];
        }
        subj2coords[r.subject_id].push({"x":xds(r.subject_event_day), "y":ds(r.total)});
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

    resizeChart() {
      const { width, height } = this.container.getBoundingClientRect();
      this.height = height;
      // HACK
      this.width = 500;
      // this.context.scale(this.devicePixelRatio, this.devicePixelRatio);
    },
    drawMultiCurve(coords, color, alpha) {
      const { context } = this;
      context.lineWidth = 1;
      context.strokeStyle = color;
      context.globalAlpha = alpha;

      context.beginPath();
      var lastCoords = undefined;

      // TODO - truncate curves/lines at right axis
      
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
      context.stroke();
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
//        console.log("cohort keys = " + Object.keys(c));
     
        // determine which subjects are in the cohort
        const xf = crossfilter(slf.data);
        console.log("data[0] = " + Object.keys(slf.data[0]));

        // add dimensions and filters
        // xf.dimension(dim);
        // dim.filterFunction(filter);

        c.queries.forEach(function(q) {
          // adapted from FIND_COHORT_QUERY
          const inputVariable = q.input_variable;
          var filter_fn = undefined;
          let accessor = undefined;
          let dim = undefined;

          if (q.input_variable.subject_ontology === undefined) {
//            console.log("trying to get observation_ontology_id " + q.input_variable.observation_ontology.id);
            // convert dimension_label to data field name
            let subfield = dimension2field[q.input_variable.dimension_label];
            accessor = function(d) { return d[q.input_variable.observation_ontology.id][subfield] };
            dim = xf.dimension(accessor);
          } else {
            let lbl = q.input_variable.subject_ontology.label;
            // special case for study
            if (lbl === "Study") {
               accessor = function(d) { return d["study"]["study_name"] };
            } else {
               accessor = function(d) { return d[lbl] };
            }
//            console.log("trying to get subject_ontology_id " + q.input_variable.subject_ontology.label);
            dim = xf.dimension(accessor);
          }

          if ((q.value !== undefined) && (q.value !== null)) {
            filter_fn = function(d) { console.log("eq filter got " + d + " checking against " + q.value); return d === q.value; };
//            console.log("adding filter for " + q.input_variable.observation_ontology.label + "=" + q.value);
            dim.filterFunction(filter_fn);
          } else if ((q.min_value !== undefined) && (q.max_value !== undefined)) {
            filter_fn = function(d) { console.log("lte/gte filter got " + d + " checking against min=" + q.min_value + " max=" + q.max_value); return ((d >= q.min_value) && (d <= q.max_value)); };
//            console.log("adding filter for " + q.input_variable.subject_ontology.label + ">=" + q.min_value + " <=" + q.max_value);
            dim.filterFunction(filter_fn);
          } else {
            console.log("unsupported query " + q);
          }
        });

        const filt = xf.allFiltered();

        let sids = {};
        filt.forEach(function(r) {
          sids[r.subject_id] = 1;
        });

        var cohort_subject_ids = Object.keys(sids);
        var paths = slf.getRawPaths(cohort_subject_ids);
        console.log("got " + paths.length + " paths for cohort " + c.label);
        paths.forEach(path => slf.drawMultiCurve(path, c.color, 0.45));
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
          this.dimensionScale(0) + tickSize + tickPadding
        );
      });

      this.context.fillText(
        "time in days since first visit",
        this.xDimensionScale(xmax/2),
        this.dimensionScale(0) + ( tickSize + tickPadding) * 2
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
