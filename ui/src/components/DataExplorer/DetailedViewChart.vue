<template>
  <v-container ref="dv_container" v-resize="onResize" fluid class="pa-0 ma-0">
    <v-row class="pa-0 ma-0">
      <v-col cols="12" class="pa-0 ma-0">
        <!-- Detailed View Chart -->
        <canvas
          ref="dv_canvas"
          :width="width"
          :height="height"
          class="pa-0 ma-0"
        >
        </canvas>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';
import { scaleLinear, scaleBand } from 'd3-scale';
import { select } from 'd3-selection';
import { max, mean, deviation } from 'd3-array';
import { sortByVisitEvent, sortVisitEvents } from '@/utils/helpers';
import { colors } from '@/utils/colors';

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
    drawRaw: {
      type: Boolean,
      required: false,
      default: true,
    },
    drawMean: {
      type: Boolean,
      required: false,
      default: true,
    },
    showPopulationCounts: {
      type: Boolean,
      required: false,
      default: false,
    },
    showFirstLastVisit: {
      type: Boolean,
      required: false,
      default: false,
    },
    xaxis: {
      type: String,
      required: true,
    },
    minHeight: {
      type: Number,
      required: false,
      default: 400,
    },
    minWidth: {
      type: Number,
      required: false,
      default: 550,
    },
  },
  data() {
    return {
      devicePixelRatio: 1,
      width: 0,
      height: 0,
      initialWidth: 0,
      initialHeight: 0,
      margin: { top: 20, right: 75, bottom: 100, left: 75 },
      tick_font: '15px sans-serif',
      label_font: '20px sans-serif',
      y_axis_pad_frac: 0.1,
      colors: colors,
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
    // get raw data, *for a specific variable/dimension*
    getRawData() {
      const filtered = this.rawData.filter(
        d => d.observation_ontology_id === this.dimensionName
      );

      // group by subject id
      const subj2data = {};
      filtered.forEach(r => {
        if (!(r.subject_id in subj2data)) {
          subj2data[r.subject_id] = [];
        }
        subj2data[r.subject_id].push(r);
      });

      // compute subject-relative time in days
      Object.keys(subj2data).forEach(k => {
        const rows = subj2data[k];
        const srows = rows.sort((a, b) => a.event_day - b.event_day);
        const firstDay = srows[0].event_day;
        let ind = 1;
        rows.forEach(r => {
          r.subject_event_day = r.event_day - firstDay;
          r.subject_event_index = ind;
          ind += 1;
          // TODO - subject_event_index may differ from visit_num
        });
      });

      // sort by visit event
      var visit_evt_fn = x => x.visit_event;
      var sorted = sortByVisitEvent(filtered, visit_evt_fn);
      return sorted;
    },
    yAxisRangeMax() {
      const rd = this.getRawData;
      const rmax = max(rd, d => d.value * 1.0);
      return rmax * (1 + this.y_axis_pad_frac);
    },

    // --------------------------------------------------
    // x-axis
    // --------------------------------------------------
    xaccessor() {
      if (this.xaxis === 'visit_event') {
        return x => x.visit_event;
      } else if (this.xaxis === 'visit_num') {
        return x => x.visit_num;
      }
      if (this.xaxis === 'days') {
        return function(x) {
          return x.subject_event_day;
        };
      }
      return function(x) {
        return x.subject_event_index;
      };
    },
    timepoints() {
      // timepoints for current variable only
      //      const rd = this.getRawData;
      // return all timepoints
      const rd = this.rawData;
      const timepoints = {};
      const xacc = this.xaccessor;
      var numericEvents = true;
      rd.forEach(x => {
        var xa = xacc(x);
        if (isNaN(xa)) {
          numericEvents = false;
        }
        timepoints[xa] = 1;
      });
      return sortVisitEvents(Object.keys(timepoints));
    },
    xmin() {
      const tp = this.timepoints;
      return tp[0];
    },
    xmax() {
      const tp = this.timepoints;
      return tp[tp.length - 1];
    },
    xDimensionScale() {
      const tp = this.timepoints;
      return scaleBand()
        .domain(tp)
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
    drawRaw() {
      this.updateCanvas();
    },
    drawMean() {
      this.updateCanvas();
    },
    showPopulationCounts() {
      this.updateCanvas();
    },
    showFirstLastVisit() {
      this.updateCanvas();
    },
    cohorts() {
      this.updateCanvas();
    },
    visibleCohorts() {
      this.updateCanvas();
    },
  },
  created() {
    this.devicePixelRatio = window.devicePixelRatio || 1;
  },
  mounted() {
    this.container = this.$refs.dv_container;

    //console.log("mounted, container height = " + this.container.clientHeight + " width=" + this.container.clientWidth);
    this.initialHeight = this.container.clientHeight;
    this.initialWidth = this.container.clientWidth;

    this.canvas = this.$refs.dv_canvas;

    //console.log("mounted, canvas height = " + this.canvas.clientHeight + " width=" + this.canvas.clientWidth);

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
    onResize() {
      this.resizeChart();
      this.$nextTick(() => this.updateCanvas());
    },

    selectedCohorts() {
      const cch = [];
      const cid = this.collection.id;
      this.visibleCohorts.forEach(e => {
        if (e.collection_id === cid) {
          cch.push(e);
        }
      });
      return cch;
    },

    cohortsHaveSubjects() {
      const cohorts = this.selectedCohorts();
      let haveSubjects = true;
      cohorts.forEach(c => {
        if (typeof c.subject_ids === 'undefined') {
          haveSubjects = false;
        }
      });
      return haveSubjects;
    },

    getRawPaths(subjectIds) {
      const rd = this.getRawData;
      const xds = this.xDimensionScale;
      const ds = this.dimensionScale;
      const xacc = this.xaccessor;

      // group raw data by subject id
      const subj2coords = {};
      rd.forEach(r => {
        if (!(r.subject_id in subj2coords)) {
          subj2coords[r.subject_id] = [];
        }
        subj2coords[r.subject_id].push({
          x: xds(xacc(r)),
          y: ds(r.value * 1.0),
        });
      });

      // extract paths for each subject
      const paths = [];
      subjectIds.forEach(k => {
        const coords = subj2coords[k];
        if (coords !== undefined) {
          paths.push(coords);
        }
      });
      return paths;
    },

    getMeanAndSDPaths(subjectIds) {
      const rd = this.getRawData;
      const xds = this.xDimensionScale;
      const ds = this.dimensionScale;
      const xacc = this.xaccessor;
      const sjids = {};
      subjectIds.forEach(sid => {
        sjids[sid] = 1;
      });

      // group raw data by timepoint, filtering by subject_id
      const tp2data = {};
      rd.forEach(r => {
        if (!(r.subject_id in sjids)) {
          return;
        }
        const tp = xacc(r);
        if (!(tp in tp2data)) {
          tp2data[tp] = [];
        }
        tp2data[tp].push(r.value * 1.0);
      });

      // extract paths for mean and mean +/- SD
      const meanPath = [];
      const meanMinusSDPath = [];
      const meanPlusSDPath = [];
      const tpts = this.timepoints;

      tpts.forEach(tp => {
        if (tp in tp2data) {
          const data = tp2data[tp];
          const mn = mean(data);
          let sd = deviation(data);
          // TODO - determine whether this is the best approach - normally sd is undefined for a sample of size 1
          if (sd === undefined) {
            sd = 0;
          }
          //          console.log("tp= " + tp + " data.length=" + data.length);
          const xp = xds(tp);
          meanPath.push({ x: xp, y: ds(mn) });
          meanMinusSDPath.push({ x: xp, y: ds(mn - sd) });
          meanPlusSDPath.push({ x: xp, y: ds(mn + sd) });
        }
      });

      return [meanPath, meanMinusSDPath, meanPlusSDPath];
    },

    resizeChart() {
      if (this.container == null) {
        return;
      }
      var { width, height } = this.container.getBoundingClientRect();
      //      console.log("resizeChart() client height = " + height + " width = " + width);

      // establish minimum size
      if (height < this.minHeight) {
        height = this.minHeight;
      }
      if (width < this.minWidth) {
        width = this.minWidth;
      }

      //      console.log("resizeChart() setting this.height = " + height + " this.width = " + width);
      // HACK - needs to be fixed properly
      this.height = height - 7;
      this.width = width;

      // this.context.scale(this.devicePixelRatio, this.devicePixelRatio);
    },

    traceMultiCurve(context, coords) {
      let lastCoords;

      // TODO - use clip rect to truncate curves/lines at right axis

      // bezier curves
      if (this.lineStyle === 'bezier') {
        coords.forEach(c => {
          if (lastCoords === undefined) {
            context.moveTo(coords[0].x, coords[0].y);
          } else {
            context.bezierCurveTo(
              lastCoords.x + (c.x - lastCoords.x) / 4,
              lastCoords.y,
              c.x - (c.x - lastCoords.x) / 4,
              c.y,
              c.x,
              c.y
            );
          }
          lastCoords = c;
        });
      }
      // straight lines
      else {
        coords.forEach(c => {
          if (lastCoords === undefined) {
            context.moveTo(coords[0].x, coords[0].y);
          } else {
            context.lineTo(c.x, c.y);
          }
          lastCoords = c;
        });
      }
    },

    drawMultiCurve(coords, color, alpha, lineWidth = 1) {
      const { context } = this;
      const savedLineWidth = context.lineWidth;
      context.lineWidth = lineWidth;
      context.strokeStyle = color;
      context.globalAlpha = alpha;

      context.beginPath();
      this.traceMultiCurve(context, coords);

      context.stroke();
      context.lineWidth = savedLineWidth;
      context.globalAlpha = 1;
    },

    drawMultiCurveRegion(
      coords1,
      coords2,
      strokeColor,
      fillColor,
      alpha,
      lineWidth = 1
    ) {
      const { context } = this;
      const savedLineWidth = context.lineWidth;
      const savedFillColor = context.fillStyle;
      const savedStrokeColor = context.strokeStyle;

      context.lineWidth = lineWidth;
      context.strokeStyle = strokeColor;
      context.globalAlpha = alpha;
      context.fillStyle = fillColor;

      context.beginPath();

      this.traceMultiCurve(context, coords1);
      context.lineTo(
        coords2[coords2.length - 1].x,
        coords2[coords2.length - 1].y
      );
      this.traceMultiCurve(context, coords2.reverse());
      context.lineTo(coords1[0].x, coords1[0].y);

      context.fill();
      context.stroke();
      context.lineWidth = savedLineWidth;
      context.fillStyle = savedFillColor;
      context.strokeStyle = savedStrokeColor;
      context.globalAlpha = 1;
    },

    drawData() {
      const cohorts = this.selectedCohorts();
      const slf = this;

      // draw all raw data
      if (slf.drawRaw) {
        cohorts.forEach(c => {
          const cohortSubjectIds = c.subject_ids;
          if (typeof cohortSubjectIds !== 'undefined') {
            // draw single path for each subject
            const paths = slf.getRawPaths(cohortSubjectIds);
            const rawOpacity = slf.drawMean ? 0.3 : 0.5;
            paths.forEach(path => {
              slf.drawMultiCurve(path, c.color, rawOpacity);
            });
          }
        });
      }

      if (slf.drawMean) {
        const groups = [];

        // get all paths
        cohorts.forEach(c => {
          const cohortSubjectIds = c.subject_ids;
          if (typeof cohortSubjectIds !== 'undefined') {
            // draw mean and standard deviation for entire group
            const paths = slf.getMeanAndSDPaths(cohortSubjectIds);
            groups.push({ paths, color: c.color });
          }
        });

        // shade +/- 1 SD regions
        groups.forEach(g => {
          slf.drawMultiCurveRegion(
            g.paths[1],
            g.paths[2],
            'black',
            '#d0d0d0',
            0.4,
            0.5
          );
        });

        // draw +/- 1 SD outlines
        groups.forEach(g => {
          slf.drawMultiCurve(g.paths[1], g.color, 0.7, 1);
          slf.drawMultiCurve(g.paths[2], g.color, 0.7, 1);
        });

        // draw group means
        groups.forEach(g => {
          slf.drawMultiCurve(g.paths[0], g.color, 0.7, 8);
        });
      }
    },

    drawSubjectCountsVerticalAxis(yscale, maxSubjects, which, xOffset) {
      const tickCount = 3;
      const tickSize = 6;
      const ticks = yscale.ticks(tickCount);
      const tickFormat = yscale.tickFormat(tickCount);
      let x1 = xOffset;
      let x2 = xOffset - tickSize;
      let tickOffset = -3;
      let textAlign = 'right';

      if (which === 'right') {
        x1 = this.computedWidth + xOffset;
        x2 = this.computedWidth + xOffset + tickSize;
        tickOffset = 3;
        textAlign = 'left';
      }
      this.context.font = this.tick_font;
      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(x1, yscale(d));
        this.context.lineTo(x2, yscale(d));
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = textAlign;
      this.context.textBaseline = 'middle';
      ticks.forEach(d => {
        this.context.fillText(tickFormat(d), x2 + tickOffset, yscale(d));
      });
    },

    // plot number of subjects at each timepoint/visit
    // TODO - move computation of subject counts out of the draw loop
    drawSubjectCounts() {
      const rd = this.getRawData;
      const selCohorts = this.selectedCohorts();
      const xacc = this.xaccessor;
      const tpts = this.timepoints;

      // count total number of subject ids at each timepoint
      const tp2subjIds = {};
      rd.forEach(r => {
        var evt = xacc(r);
        if (!(evt in tp2subjIds)) {
          tp2subjIds[evt] = {};
        }
        tp2subjIds[evt][r.subject_id] = 1;
      });

      const tp2subjCount = {};
      const tp2cohortSubjCounts = {};

      var maxSubjects = 0;
      Object.keys(tp2subjIds).forEach(tp => {
        var subj_ids_d = tp2subjIds[tp];
        var n_subj = Object.keys(subj_ids_d).length;

        // population count - all subjects
        tp2subjCount[tp] = n_subj;

        // per-cohort counts
        var cc = {};
        tp2cohortSubjCounts[tp] = cc;

        selCohorts.forEach(c => {
          var n_cohort_subjs = 0;
          c.subject_ids.forEach(sid => {
            if (sid in subj_ids_d) {
              n_cohort_subjs += 1;
            }
          });
          cc[c.id] = n_cohort_subjs;
          if (n_cohort_subjs > maxSubjects) {
            maxSubjects = n_cohort_subjs;
          }
        });

        if (this.showPopulationCounts) {
          if (n_subj > maxSubjects) {
            maxSubjects = n_subj;
          }
        }
      });

      const yscale = scaleLinear()
        .domain([0, maxSubjects])
        .range([this.computedHeight + 90, this.computedHeight + 40]);

      const xOffset =
        -(this.xDimensionScale(tpts[1]) - this.xDimensionScale(tpts[0])) / 2.0;

      this.drawSubjectCountsVerticalAxis(yscale, maxSubjects, 'left', xOffset);
      this.drawSubjectCountsVerticalAxis(yscale, maxSubjects, 'right', xOffset);

      // plot subject counts
      const barsWidth =
        this.xDimensionScale(tpts[1]) - this.xDimensionScale(tpts[0]) - 2;
      const nBars = selCohorts.length + (this.showPopulationCounts ? 1 : 0);
      const barWidth = barsWidth / nBars;
      const xscale = this.xDimensionScale;

      const drawBar = function(
        context,
        time,
        barnum,
        startSubjCount,
        endSubjCount,
        color,
        opacity = 1
      ) {
        context.fillStyle = color;
        context.strokeStyle = 'white';
        context.globalAlpha = opacity;
        context.beginPath();
        const x1 = xOffset + xscale(time) + barnum * barWidth;
        const x2 = x1 + barWidth;
        const y1 = yscale(startSubjCount);
        const y2 = yscale(endSubjCount);
        context.moveTo(x1, y1);
        context.lineTo(x1, y2);
        context.lineTo(x2, y2);
        context.lineTo(x2, y1);
        context.lineTo(x1, y1);
        context.fill();
        context.stroke();
        context.globalAlpha = 1;
      };

      this.context.font = this.label_font;
      tpts.forEach(tpt => {
        let barnum = 0;

        // study population count
        const subjCount = tp2subjCount[tpt];
        if (this.showPopulationCounts) {
          drawBar(this.context, tpt, barnum, 0, subjCount, '#F8D580', 0.7);
          barnum += 1;
        }

        // using multiple bar graph instead of stacked bar graph because the cohorts are not necessarily disjoint
        const bars = [];

        selCohorts.forEach(c => {
          if (tpt in tp2cohortSubjCounts) {
            const sc = tp2cohortSubjCounts[tpt][c.id];
            bars.push({ tp: tpt, score: sc, color: c.color });
          }
        });

        // TODO - sort bars in same order that cohorts are listed in Cohorts panel?
        bars.forEach(b => {
          drawBar(this.context, b.tp, barnum, 0, b.score, b.color);
          barnum += 1;
        });
      });

      // bottom margin caption
      this.context.strokeStyle = 'black';
      this.context.fillStyle = 'black';
      this.context.textAlign = 'center';

      this.context.fillText(
        'number of subjects with measurements',
        (xscale(tpts[0]) + xscale(tpts[tpts.length - 1])) / 2,
        yscale(0) + 12
      );
    },

    highlightFirstAndLastVisit(yscale) {
      var tpts = this.timepoints;
      var xscale = this.xDimensionScale;
      var yscale = this.dimensionScale;
      var cheight = this.computedHeight + 30;

      const drawHighlight = function(
        context,
        time,
        barWidth,
        color,
        opacity = 1
      ) {
        context.fillStyle = color;
        context.strokeStyle = 'white';
        context.globalAlpha = opacity;
        context.beginPath();
        const x1 = xscale(time) - barWidth / 2;
        const x2 = x1 + barWidth;
        const y1 = 0;
        const y2 = cheight;
        context.moveTo(x1, y1);
        context.lineTo(x1, y2);
        context.lineTo(x2, y2);
        context.lineTo(x2, y1);
        context.lineTo(x1, y1);
        context.fill();
        context.stroke();
        context.globalAlpha = 1;
      };

      // highlight first/last visit
      var obs_vars = this.collection.observation_variables_list.filter(
        ov => ov.ontology.id === this.dimensionName
      );
      if (obs_vars.length === 1) {
        var barWidth = xscale(tpts[1]) - xscale(tpts[0]);

        var fve = obs_vars[0].first_visit_event;
        drawHighlight(
          this.context,
          fve,
          barWidth,
          colors['firstVisit'],
          colors['firstVisit-opacity']
        );

        var lve = obs_vars[0].last_visit_event;
        drawHighlight(
          this.context,
          lve,
          barWidth,
          colors['lastVisit'],
          colors['lastVisit-opacity']
        );
      }
      this.context.strokeStyle = 'black';
      this.context.fillStyle = 'black';
    },

    drawLeftAxis() {
      const tickCount = 10;
      const tickSize = 6;
      const tickPadding = 3;
      const ticks = this.dimensionScale.ticks(tickCount);
      const tickFormat = this.dimensionScale.tickFormat(tickCount);

      this.context.font = this.tick_font;
      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(0, this.dimensionScale(d));
        this.context.lineTo(-6, this.dimensionScale(d));
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(0.5, 0);
      this.context.lineTo(0.5, this.computedHeight);
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
    },
    drawRightAxis() {
      const tickCount = 10;
      const tickSize = 6;
      const tickPadding = 3;
      const ticks = this.dimensionScale.ticks(tickCount);
      const tickFormat = this.dimensionScale.tickFormat(tickCount);
      const { xmax } = this;

      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(this.xDimensionScale(xmax), this.dimensionScale(d));
        this.context.lineTo(
          this.xDimensionScale(xmax) + tickSize,
          this.dimensionScale(d)
        );
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(this.xDimensionScale(xmax) + 0.5, 0);
      this.context.lineTo(
        this.xDimensionScale(xmax) + 0.5,
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
    },
    drawBottomAxis() {
      let tickCount = 10;
      const tickSize = 6;
      const tickPadding = 4;
      const tp = this.timepoints;
      const { xmax } = this;

      if (this.xaxis !== 'days') {
        tickCount = tp.length;
      }

      const scale = this.xDimensionScale;

      this.context.beginPath();
      tp.forEach(d => {
        this.context.moveTo(this.xDimensionScale(d), this.dimensionScale(0));
        this.context.lineTo(
          this.xDimensionScale(d),
          this.dimensionScale(0) + tickSize
        );
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(this.xDimensionScale(this.xmin), this.computedHeight);
      this.context.lineTo(
        this.xDimensionScale(xmax) + 0.5,
        this.computedHeight
      );
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = 'center';
      this.context.textBaseline = 'middle';
      tp.forEach(d => {
        this.context.fillText(
          d,
          this.xDimensionScale(d),
          this.dimensionScale(0) + tickSize + tickPadding * 2
        );
      });

      let caption = 'visit number';
      if (this.xaxis === 'days') {
        caption = 'time in days since first visit';
      }

      this.context.font = this.label_font;
      this.context.fillText(
        caption,
        this.xDimensionScale(xmax / 2),
        this.dimensionScale(0) + (tickSize + tickPadding) * 3
      );
    },
    drawAxes() {
      this.drawLeftAxis();
      this.drawRightAxis();
      this.drawBottomAxis();
    },
    updateCanvas() {
      // TODO - adding 50 is a workaround to account for the right-hand axis, which is outside of the computed area
      this.context.clearRect(
        0,
        0,
        this.computedWidth + this.margin.left + 50,
        this.computedHeight + 120
      );
      if (this.cohortsHaveSubjects()) {
        this.context.translate(this.margin.left, 0);
        this.drawData();
        this.drawAxes();
        this.drawSubjectCounts();
        if (this.showFirstLastVisit) {
          this.highlightFirstAndLastVisit();
        }
        this.context.translate(-this.margin.left, 0);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
div .container {
  padding: 0px important;
}
</style>
