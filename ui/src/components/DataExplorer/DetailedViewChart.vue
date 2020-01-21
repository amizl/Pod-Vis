<template>
  <v-flex ref="container" fill-height>
    <!-- Detailed View Chart -->
    <canvas ref="canvas" :width="width" :height="height" min-height="500">
    </canvas>
  </v-flex>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';
import { scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
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
    drawRaw: {
      type: Boolean,
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
      margin: { top: 20, right: 50, bottom: 100, left: 50 },
      tick_font: "15px sans-serif",
      label_font: "20px sans-serif",
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

      return filtered;
    },
    yAxisRangeMax() {
      const rd = this.getRawData;
      const rmax = max(rd, d => d.total);
      return rmax;
    },

    // --------------------------------------------------
    // x-axis
    // --------------------------------------------------
    xaccessor() {
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
      const rd = this.getRawData;
      const timepoints = {};
      const xacc = this.xaccessor;
      rd.forEach(x => {
        timepoints[xacc(x)] = 1;
      });
      return Object.keys(timepoints).sort((a, b) => a - b);
    },
    xmin() {
      const tp = this.timepoints;
      return tp[0];
    },
    xmax() {
      const tp = this.timepoints;
      // TODO - allow user to adjust xmax up to the limit
      return tp[tp.length - 1];
    },
    xDimensionScale() {
      return scaleLinear()
        .domain([this.xmin, this.xmax])
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
        subj2coords[r.subject_id].push({ x: xds(xacc(r)), y: ds(r.total) });
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
        tp2data[tp].push(r.total);
      });

      // extract paths for mean and mean +/- SD
      const meanPath = [];
      const meanMinusSDPath = [];
      const meanPlusSDPath = [];

      const sortedTp = Object.keys(tp2data).sort((a, b) => a - b);

      sortedTp.forEach(tp => {
        const data = tp2data[tp];
        const mn = mean(data);
        let sd = deviation(data);
        // TODO - determine whether this is the best approach - normally sd is undefined for a sample of size 1
        if (sd === undefined) {
          sd = 0;
        }
        const xp = xds(tp);
        meanPath.push({ x: xp, y: ds(mn) });
        meanMinusSDPath.push({ x: xp, y: ds(mn - sd) });
        meanPlusSDPath.push({ x: xp, y: ds(mn + sd) });
      });

      return [meanPath, meanMinusSDPath, meanPlusSDPath];
    },

    resizeChart() {
      const { height } = this.container.getBoundingClientRect();
      this.height = height;
      // HACK - establish minimum size
      if (height < 400) {
        this.height = 400;
      }
      this.width = 550;
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

    drawSubjectCountsVerticalAxis(yscale, maxSubjects, which) {
      const tickCount = 3;
      const tickSize = 6;
      const ticks = yscale.ticks(tickCount);
      const tickFormat = yscale.tickFormat(tickCount);
      let x1 = 0;
      let x2 = -tickSize;
      let tickOffset = -3;
      let textAlign = 'right';

      if (which === 'right') {
        x1 = this.computedWidth;
        x2 = this.computedWidth + tickSize;
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

    // plot number of subjects remaining at each timepoint/visit
    // TODO - move computation of subject counts out of the draw loop
    drawSubjectCounts() {
      const rd = this.getRawData;
      const cohorts = this.selectedCohorts();
      const xacc = this.xaccessor;
      let tickCount = 10;
      const tpts = this.timepoints;

      // compute last timepoint for each subject
      const subj2lasttp = {};
      rd.forEach(r => {
        if (
          !(r.subject_id in subj2lasttp) ||
          subj2lasttp[r.subject_id] < xacc(r)
        ) {
          subj2lasttp[r.subject_id] = xacc(r);
        }
      });

      const maxSubjects = Object.keys(subj2lasttp).length;

      // map timepoint to list of subjects for whom it is the last visit
      const last2subjects = {};
      Object.keys(subj2lasttp).forEach(sid => {
        const tp = subj2lasttp[sid];
        if (!(tp in last2subjects)) {
          last2subjects[tp] = [];
        }
        last2subjects[tp].push(sid);
      });

      // map timepoint to remaining subjects in each cohort
      const tp2ccounts = {};

      const ccounts = {};
      ccounts.population = {};
      Object.keys(subj2lasttp).forEach(x => {
        ccounts.population[x] = 1;
      });
      cohorts.forEach(c => {
        ccounts[c.label] = {};
        c.subject_ids.forEach(sid => {
          ccounts[c.label][sid] = 1;
        });
      });

      Object.keys(last2subjects)
        .sort((a, b) => a - b)
        .forEach(tp => {
          // shallow copy
          tp2ccounts[tp] = {
            population: Object.assign({}, ccounts.population),
          };
          cohorts.forEach(c => {
            tp2ccounts[tp][c.label] = Object.assign({}, ccounts[c.label]);
          });

          // update cohorts, including total population
          const subjids = last2subjects[tp];
          subjids.forEach(x => {
            delete ccounts.population[x];
            cohorts.forEach(c => {
              delete ccounts[c.label][x];
            });
          });
        });

      if (this.xaxis === 'visits') {
        tickCount = tpts.length;
      }
      const xscale = scaleLinear()
        .domain([this.xmin, this.xmax])
        .range([0, this.computedWidth]);
      const yscale = scaleLinear()
        .domain([0, maxSubjects])
        .range([this.computedHeight + 90, this.computedHeight + 40]);
      const ticks = xscale.ticks(tickCount);

      // add missing timepoints to tp2ccounts
      let lastTp = -1;
      let tnum = 0;
      Object.keys(tp2ccounts)
        .sort((a, b) => a - b)
        .forEach(tp => {
          while (ticks[tnum] <= tp) {
            tp2ccounts[ticks[tnum]] = tp2ccounts[tp];
            tnum += 1;
          }
          lastTp = tp;
        });

      this.drawSubjectCountsVerticalAxis(yscale, maxSubjects, 'left');
      this.drawSubjectCountsVerticalAxis(yscale, maxSubjects, 'right');

      // plot subject counts
      const barsWidth = xscale(ticks[1]) - xscale(ticks[0]) - 2;
      const nBars = cohorts.length + 1;
      const barWidth = barsWidth / nBars;

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
        const x1 = xscale(time) + barnum * barWidth;
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
      ticks.forEach(d => {
        if (d >= this.xmax) return;
        let barnum = 0;

        // population
        const subjCount = Object.keys(tp2ccounts[d].population).length;
        drawBar(this.context, d, barnum, 0, subjCount, '#F8D580', 0.7);
        barnum += 1;

        // using multiple bar graph instead of stacked bar graph because the cohorts are not disjoint
        const bars = [];

        cohorts.forEach(c => {
          const sc = Object.keys(tp2ccounts[d][c.label]).length;
          bars.push({ tp: d, score: sc, color: c.color });
        });

        // TODO - sort bars in same order that cohorts are listed in Cohorts panel?
        bars.forEach(b => {
          drawBar(this.context, b.tp, barnum, 0, b.score, b.color);
          barnum += 1;
        });
      });

      this.context.strokeStyle = 'black';
      this.context.fillStyle = 'black';
      this.context.textAlign = 'center';

      this.context.fillText(
        'number of subjects remaining',
        xscale(this.xmax / 2),
        yscale(0) + 12
      );
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

      if (this.xaxis === 'visits') {
        tickCount = tp.length;
      }

      const scale = scaleLinear()
        .domain([this.xmin, this.xmax])
        .range([0, this.computedWidth]);
      const ticks = scale.ticks(tickCount);
      const tickFormat = scale.tickFormat(tickCount);

      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(scale(d), this.dimensionScale(0));
        this.context.lineTo(scale(d), this.dimensionScale(0) + tickSize);
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
      ticks.forEach(d => {
        this.context.fillText(
          tickFormat(d),
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
        this.context.translate(-this.margin.left, 0);
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
