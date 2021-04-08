<template>
  <v-container
    ref="dv_container"
    v-resize="onResize"
    fluid
    fill-width
    width="100%"
    class="pa-0 ma-0"
  >
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
import { min, max, mean, deviation } from 'd3-array';
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
    visibleCohorts: {
      type: Array,
      required: true,
      default: () => [],
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
    showAllTimepoints: {
      type: Boolean,
      required: false,
      default: false,
    },
    showPercentages: {
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
    barGroupGapPercent: {
      type: Number,
      required: false,
      default: 15,
    },
  },
  data() {
    return {
      devicePixelRatio: 1,
      width: 0,
      height: 0,
      initialWidth: 0,
      initialHeight: 0,
      margin: { top: 20, right: 100, bottom: 150, left: 100 },
      tick_font: '15px sans-serif',
      label_font: '18px sans-serif',
      colors: colors,
      maxSubjects: 0,
      maxTotalSubjects: 0,
      tp2subjCount: {},
      tp2cohortSubjCounts: {},
      tp2cohortSubjCategoryCounts: {},
      categoryColorKey: [],
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      data: state.DATA,
      rawData: state.RAW_DATA,
      cohorts: state.COHORTS,
      collection: state.COLLECTION,
    }),

    // --------------------------------------------------
    // y-axis
    // --------------------------------------------------
    yAxisRangeMax() {
      var rmax = null;

      // use total subject count for categorical vars
      if (this.isCategorical) {
        if (this.showPercentages) return 100;
        return this.maxSubjects;
      }

      // maximum raw data value
      const rd = this.getRawData(true);
      const rawmax = max(rd, d => d.value * 1.0);
      if (this.drawRaw && (rmax == null || rawmax > rmax)) {
        rmax = rawmax;
      }

      // maximum average data value (mean + 1 SD)
      var avgmax = null;
      var tp_msd = this.timepointsMeanAndSD;
      const timepoints = this.timepoints;

      timepoints.forEach(tp => {
        if (tp in tp_msd) {
          this.collectionCohorts.forEach(c => {
            if (c.id in tp_msd[tp]) {
              var d = tp_msd[tp][c.id];
              var mv = d['mean'] + d['SD'];
              if (avgmax == null || mv > avgmax) {
                avgmax = mv;
              }
            }
          });
        }
      });
      if (this.drawMean && (rmax == null || avgmax > rmax)) {
        rmax = avgmax;
      }
      return rmax;
    },
    yAxisRangeMin() {
      if (this.isCategorical) {
        return 0;
      }

      var rmin = null;

      // minimum raw data value
      const rd = this.getRawData(true);
      const rawmin = min(rd, d => d.value * 1.0);
      if (this.drawRaw && (rmin == null || rawmin < rmin)) {
        rmin = rawmin;
      }

      // minimum average data value (mean - 1 SD)
      var avgmin = null;
      var tp_msd = this.timepointsMeanAndSD;
      const timepoints = this.timepoints;
      timepoints.forEach(tp => {
        if (tp in tp_msd) {
          this.collectionCohorts.forEach(c => {
            if (c.id in tp_msd[tp]) {
              var d = tp_msd[tp][c.id];
              var mv = d['mean'] - d['SD'];
              if (avgmin == null || mv < avgmin) {
                avgmin = mv;
              }
            }
          });
        }
      });
      if (this.drawMean && (rmin == null || avgmin < rmin)) {
        rmin = avgmin;
      }
      return rmin;
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
      // show all timepoints or only timepoints for visible cohorts
      const rd = this.showAllTimepoints ? this.rawData : this.getRawData(true);
      const timepoints = {};
      const xacc = this.xaccessor;
      rd.forEach(x => {
        var xa = xacc(x);
        timepoints[xa] = 1;
      });
      return sortVisitEvents(Object.keys(timepoints));
    },
    // mean and standard deviation for each timepoint and cohort
    timepointsMeanAndSD() {
      const rd = this.getRawData(true);
      const cohorts = this.collectionCohorts;
      const xacc = this.xaccessor;
      var tp_means = {};

      // subject id to cohort ids mapping
      var sid2cids = {};
      cohorts.forEach(c => {
        if (typeof c.subject_ids !== 'undefined') {
          c.subject_ids.forEach(sid => {
            if (!(sid in sid2cids)) {
              sid2cids[sid] = [];
            }
            sid2cids[sid].push(c.id);
          });
        }
      });

      // group raw data by timepoint and cohort
      const tp2data = {};
      rd.forEach(r => {
        if (r.subject_id in sid2cids) {
          var cids = sid2cids[r.subject_id];
          const tp = xacc(r);
          if (!(tp in tp2data)) {
            tp2data[tp] = {};
          }
          cids.forEach(cid => {
            if (!(cid in tp2data[tp])) {
              tp2data[tp][cid] = [];
            }
            tp2data[tp][cid].push(r.value * 1.0);
          });
        }
      });

      const timepoints = this.timepoints;
      // iterate over timepoints and cohorts, compute mean, SD
      timepoints.forEach(tp => {
        if (!(tp in tp_means)) {
          tp_means[tp] = {};
        }
        cohorts.forEach(c => {
          if (tp in tp2data && c.id in tp2data[tp]) {
            var data = tp2data[tp][c.id];
            const mn = mean(data);
            let sd = deviation(data);
            // TODO - determine whether this is the best approach - normally sd is undefined for a sample of size 1
            if (sd === undefined) {
              sd = 0;
            }
            tp_means[tp][c.id] = { mean: mn, SD: sd };
          }
        });
      });

      return tp_means;
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

      // add padding to allow bar charts to fit
      //      if (this.isCategorical) {
      const ntp = tp.length;
      const bw = this.computedWidth / (ntp - 1);
      const hbw = bw / 2;
      return scaleBand()
        .domain(tp)
        .range([hbw, this.computedWidth + hbw]);
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
        .domain([this.yAxisRangeMin, this.yAxisRangeMax])
        .range(
          this.variable.flip_axis
            ? [this.margin.top, this.computedHeight]
            : [this.computedHeight, 10]
        );
      return scale;
    },
    collectionCohorts() {
      const cch = [];
      const th = this;
      this.cohorts.forEach(e => {
        if (e.collection_id === th.collection.id) {
          cch.push(e);
        }
      });
      return cch;
    },
    isCategorical() {
      return this.variable && this.variable.data_category == 'Categorical';
    },
    barGroupWidth() {
      const tpts = this.timepoints;
      const xds = this.xDimensionScale;
      return xds(tpts[1]) - xds(tpts[0]);
    },
    barGroupGap() {
      return this.barGroupWidth * (this.barGroupGapPercent / 100.0);
    },
  },
  watch: {
    rawData() {
      this.updateSubjectCounts();
      this.updateCanvas();
    },
    dimensionName() {
      this.updateSubjectCounts();
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
      this.updateSubjectCounts();
      this.updateCanvas();
    },
    showFirstLastVisit() {
      this.updateCanvas();
    },
    showAllTimepoints() {
      this.updateSubjectCounts();
      this.updateCanvas();
    },
    showPercentages() {
      this.updateCanvas();
    },
    cohorts() {
      this.updateCanvas();
    },
    visibleCohorts() {
      this.updateSubjectCounts();
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
    // get raw data, *for a specific variable/dimension*
    getRawData(filterBySubjects) {
      var subj_ids = null;

      // only return data relevant to the subjects in the visible cohorts
      if (filterBySubjects) {
        subj_ids = {};
        this.visibleCohorts.forEach(c => {
          c.subject_ids.forEach(sid => {
            subj_ids[sid] = 1;
          });
        });
      }

      const filtered = this.rawData.filter(
        d =>
          d.observation_ontology_id === this.dimensionName &&
          (subj_ids == null || d.subject_id in subj_ids)
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

    onResize() {
      this.$nextTick(() => {
        this.resizeChart();
        this.$nextTick(() => {
          this.updateCanvas();
        });
      });
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
      const rd = this.getRawData(false);
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
      const rd = this.getRawData(true);
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
          const xp = xds(tp);
          meanPath.push({ x: xp, y: ds(mn) });
          meanMinusSDPath.push({ x: xp, y: ds(mn - sd) });
          meanPlusSDPath.push({ x: xp, y: ds(mn + sd) });
        }
      });

      return [meanPath, meanMinusSDPath, meanPlusSDPath];
    },

    resizeChart() {
      this.container = this.$refs.dv_container;
      if (this.container == null) {
        return;
      }
      var { width, height } = this.container.getBoundingClientRect();
      if (width == 0) {
        return;
      }

      // establish minimum size
      if (height < this.minHeight) {
        height = this.minHeight;
      }
      if (width < this.minWidth) {
        width = this.minWidth;
      }

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

    drawCohortColorKey() {
      var vm = this;
      vm.context.save();

      this.context.textAlign = 'left';
      this.context.textBaseline = 'middle';
      this.context.strokeStyle = 'black';

      const init_xoffset = -this.margin.left + 20;
      const fm = 12;
      var xoffset = init_xoffset;
      var yoffset = this.computedHeight + 125;

      this.visibleCohorts.forEach(ch => {
        this.context.fillStyle = ch.color;
        this.context.fillRect(xoffset, yoffset, 20, 20);
        this.context.fillStyle = 'black';
        this.context.fillText(ch.label, xoffset + 30, yoffset + 10);
        // new line guesstimate
        if (
          xoffset + ch.label.length * fm * 2 >
          this.computedWidth + this.margin.right
        ) {
          xoffset = init_xoffset;
          yoffset += fm * 2;
        } else {
          xoffset += ch.label.length * fm;
        }
      });

      vm.context.restore();
    },

    drawCategoryColorKey() {
      var vm = this;
      vm.context.save();

      this.context.textAlign = 'left';
      this.context.textBaseline = 'middle';

      this.categoryColorKey.forEach(ck => {
        vm.context.strokeStyle = 'black';
        vm.context.fillStyle = ck.color;
        vm.context.fillRect(ck.x, ck.y, 20, 20);
        vm.context.fillStyle = 'black';
        vm.context.fillText(ck.label, ck.x + 30, ck.y + 10);
      });

      vm.context.restore();
    },

    drawCategoricalData() {
      if (this.maxSubjects == 0) {
        this.updateSubjectCounts();
      }
      const cohorts = this.selectedCohorts();
      const tpts = this.timepoints;
      const xds = this.xDimensionScale;
      const ds = this.dimensionScale;
      const slf = this;
      const bw = this.barGroupWidth - this.barGroupGap;
      const hbw = bw / 2;
      const cbw = bw / cohorts.length;
      this.categoryColorKey = [];

      // assign colors to categories
      // TODO - copied from StackedBars.vue
      var cindex = 0;
      var ncolors = this.colors['bar_graphs'].length;
      var ck_xoffset = 0;
      var cat2color = {};
      var getBarColor = function(category) {
        // assign color to new category, add entry to color key
        if (!(category in cat2color)) {
          cat2color[category] = slf.colors['bar_graphs'][cindex % ncolors];
          cindex++;
          slf.categoryColorKey.push({
            label: category,
            color: cat2color[category],
            x: ck_xoffset,
            y: slf.computedHeight + 130,
          });
          ck_xoffset += category.length * 17;
        }
        return cat2color[category];
      };

      tpts.forEach(tp => {
        if (tp in this.tp2cohortSubjCounts) {
          const scounts = this.tp2cohortSubjCategoryCounts[tp];
          var bx = xds(tp) - hbw;
          cohorts.forEach(c => {
            if (c.id in scounts) {
              var cat_counts = scounts[c.id];
              var sorted_cats = Object.keys(cat_counts);
              sorted_cats.sort((x, y) => {
                return x.localeCompare(y);
              });
              var cumulative_count = 0;
              var cumulative_pct = 0;
              var total = 0;
              sorted_cats.forEach(cc => {
                total += cat_counts[cc];
              });

              sorted_cats.forEach(cc => {
                var count = cat_counts[cc];
                var ccolor = getBarColor(cc);
                var pct = (count / total) * 100.0;
                var y1 = ds(cumulative_count);
                var y2 = ds(cumulative_count + count);

                if (this.showPercentages) {
                  y1 = ds(cumulative_pct);
                  y2 = ds(cumulative_pct + pct);
                }

                slf.context.fillStyle = ccolor;
                this.context.fillRect(bx, y1, cbw - 1, y2 - y1);
                cumulative_count += count;
                cumulative_pct += pct;
              });
            }
            bx += cbw;
          });
        }
      });
      slf.context.fillStyle = 'black';
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
        // TODO - rework this section to make use of this.timepointsMeanAndSD
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

    updateSubjectCounts() {
      const rd = this.getRawData(false);
      const selCohorts = this.selectedCohorts();
      const xacc = this.xaccessor;

      // map subject id to cohort(s)
      const subjId2Cohorts = {};
      selCohorts.forEach(c => {
        c.subject_ids.forEach(sid => {
          if (sid in subjId2Cohorts) {
            subjId2Cohorts[sid].push(c);
          } else {
            subjId2Cohorts[sid] = [c];
          }
        });
      });
      const tp2cohortSubjCategoryCounts = {};

      // count total number of subject ids at each timepoint
      const tp2subjIds = {};
      rd.forEach(r => {
        var evt = xacc(r);
        if (!(evt in tp2subjIds)) {
          tp2subjIds[evt] = {};
        }
        tp2subjIds[evt][r.subject_id] = 1;

        // compute category counts at each timepoint
        if (r['data_category'] == 'Categorical') {
          var category = r['value'];
          if (!(evt in tp2cohortSubjCategoryCounts)) {
            tp2cohortSubjCategoryCounts[evt] = {};
          }
          var cohorts = subjId2Cohorts[r.subject_id];
          if (cohorts != null) {
            cohorts.forEach(cohort => {
              if (!(cohort.id in tp2cohortSubjCategoryCounts[evt])) {
                tp2cohortSubjCategoryCounts[evt][cohort.id] = {};
              }
              if (!(category in tp2cohortSubjCategoryCounts[evt][cohort.id])) {
                tp2cohortSubjCategoryCounts[evt][cohort.id][category] = 0;
              }
              tp2cohortSubjCategoryCounts[evt][cohort.id][category]++;
            });
          }
        }
      });

      const tp2subjCount = {};
      const tp2cohortSubjCounts = {};

      var maxSubjects = 0;
      var maxTotalSubjects = 0;

      Object.keys(tp2subjIds).forEach(tp => {
        var subj_ids_d = tp2subjIds[tp];
        var n_subj = Object.keys(subj_ids_d).length;

        // population count - all subjects
        tp2subjCount[tp] = n_subj;

        // per-cohort counts
        var cc = {};
        tp2cohortSubjCounts[tp] = cc;
        var total_subjs = 0;

        selCohorts.forEach(c => {
          var n_cohort_subjs = 0;
          c.subject_ids.forEach(sid => {
            if (sid in subj_ids_d) {
              n_cohort_subjs += 1;
            }
          });
          cc[c.id] = n_cohort_subjs;
          total_subjs += n_cohort_subjs;
          if (n_cohort_subjs > maxSubjects) {
            maxSubjects = n_cohort_subjs;
          }
        });

        if (total_subjs > maxTotalSubjects) {
          maxTotalSubjects = total_subjs;
        }

        if (this.showPopulationCounts && !this.isCategorical) {
          if (n_subj > maxSubjects) {
            maxSubjects = n_subj;
          }
        }
      });

      this.tp2subjCount = tp2subjCount;
      this.tp2cohortSubjCounts = tp2cohortSubjCounts;
      this.tp2cohortSubjCategoryCounts = tp2cohortSubjCategoryCounts;
      this.maxSubjects = maxSubjects;
      this.maxTotalSubjects = maxTotalSubjects;
    },

    // plot number of subjects at each timepoint/visit
    drawSubjectCounts() {
      if (this.maxSubjects == 0) {
        this.updateSubjectCounts();
      }

      const tpts = this.timepoints;
      const selCohorts = this.selectedCohorts();

      const yscale = scaleLinear()
        .domain([0, this.maxSubjects])
        .range([this.computedHeight + 90, this.computedHeight + 40]);

      this.drawSubjectCountsVerticalAxis(yscale, this.maxSubjects, 'left');
      this.drawSubjectCountsVerticalAxis(yscale, this.maxSubjects, 'right');

      // plot subject counts
      const barsWidth =
        this.xDimensionScale(tpts[1]) - this.xDimensionScale(tpts[0]) - 3;
      const nBars = selCohorts.length + (this.showPopulationCounts ? 1 : 0);
      const barGroupGap = this.barGroupGap;
      const hbgg = barGroupGap / 2;
      const barWidth = (barsWidth - this.barGroupGap) / nBars;
      const xscale = this.xDimensionScale;
      const xOffset = -(this.xDimensionScale.bandwidth() / 2);

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
        const x1 = xOffset + xscale(time) + barnum * barWidth + hbgg;
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
        const subjCount = this.tp2subjCount[tpt];
        if (this.showPopulationCounts) {
          drawBar(this.context, tpt, barnum, 0, subjCount, '#F8D580', 0.7);
          barnum += 1;
        }

        // using multiple bar graph instead of stacked bar graph because the cohorts are not necessarily disjoint
        const bars = [];

        selCohorts.forEach(c => {
          if (tpt in this.tp2cohortSubjCounts) {
            const sc = this.tp2cohortSubjCounts[tpt][c.id];
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

    highlightFirstAndLastVisit() {
      var tpts = this.timepoints;
      var xscale = this.xDimensionScale;
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

        var fv =
          this.xaxis == 'visit_event'
            ? obs_vars[0].first_visit_event
            : obs_vars[0].first_visit_num;
        var lv =
          this.xaxis == 'visit_event'
            ? obs_vars[0].last_visit_event
            : obs_vars[0].last_visit_num;

        if (fv != null) {
          drawHighlight(
            this.context,
            fv,
            barWidth,
            colors['firstVisit'],
            colors['firstVisit-opacity']
          );
        }
        if (lv != null) {
          drawHighlight(
            this.context,
            lv,
            barWidth,
            colors['lastVisit'],
            colors['lastVisit-opacity']
          );
        }
      }
      this.context.strokeStyle = 'black';
      this.context.fillStyle = 'black';
    },

    drawOutcomeSeverityLabels(x) {
      // "best"/"worst"
      if (!this.isCategorical) {
        // default = higher value corresponds to worse outcome/more severe disease progression
        var lmin = this.variable.flip_axis ? 'worst' : 'best';
        var lmax = this.variable.flip_axis ? 'best' : 'worst';
        this.context.save();
        this.context.font = this.label_font;
        this.context.fillText(lmin, x, this.dimensionScale(this.yAxisRangeMin));
        this.context.fillText(lmax, x, this.dimensionScale(this.yAxisRangeMax));
        this.context.restore();
      }
    },

    drawLeftAxis() {
      const tickCount = 10;
      const tickSize = 6;
      const tickPadding = 3;
      const ticks = this.dimensionScale.ticks(tickCount);
      const tickFormat = this.dimensionScale.tickFormat(tickCount);

      // line along left side of figure
      this.context.beginPath();
      this.context.moveTo(0.5, 0);
      this.context.lineTo(0.5, this.computedHeight);
      this.context.strokeStyle = 'black';
      this.context.stroke();

      if (ticks.length <= 1) return;

      // tick markings and labels
      this.context.font = this.tick_font;
      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(0, this.dimensionScale(d));
        this.context.lineTo(-6, this.dimensionScale(d));
      });
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

      // y-axis labels
      this.drawOutcomeSeverityLabels(-35);

      // y-axis caption caption
      var caption = null;
      if (this.isCategorical) {
        caption = this.showPercentages
          ? 'percentage of subjects'
          : 'number of subjects';
      } else {
        caption = this.variable.abbreviation;
      }

      const caption_y = this.computedHeight / 2.0;
      this.context.save();
      this.context.font = this.label_font;
      this.context.translate(-this.margin.left + 18, caption_y);
      this.context.rotate(-Math.PI / 2);
      this.context.textAlign = 'center';
      this.context.fillText(caption, 0, 0);
      this.context.restore();
    },
    drawRightAxis() {
      const tickCount = 10;
      const tickSize = 6;
      const tickPadding = 3;
      const ticks = this.dimensionScale.ticks(tickCount);
      const tickFormat = this.dimensionScale.tickFormat(tickCount);
      const x0 = this.computedWidth + 0.5;
      // line along right side of figure
      this.context.beginPath();
      this.context.moveTo(x0, 0);
      this.context.lineTo(x0, this.computedHeight);
      this.context.strokeStyle = 'black';
      this.context.stroke();

      if (ticks.length <= 1) return;

      // tick markings and labels
      this.context.beginPath();
      ticks.forEach(d => {
        this.context.moveTo(x0, this.dimensionScale(d));
        this.context.lineTo(x0 + tickSize, this.dimensionScale(d));
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = 'left';
      this.context.textBaseline = 'middle';
      ticks.forEach(d => {
        this.context.fillText(
          tickFormat(d),
          x0 + tickSize + tickPadding,
          this.dimensionScale(d)
        );
      });

      // "best"/"worst"
      this.drawOutcomeSeverityLabels(x0 + 35);
    },
    drawBottomAxis() {
      //      let tickCount = 10;
      const tickSize = 6;
      const tickPadding = 4;
      const tp = this.timepoints;
      const { xmax } = this;

      //      if (this.xaxis !== 'days') {
      //        tickCount = tp.length;
      //      }

      const scale = this.xDimensionScale;
      var y0 = this.computedHeight;
      var bw = scale.bandwidth();
      var hbw = bw / 2;

      this.context.beginPath();
      tp.forEach(d => {
        this.context.moveTo(this.xDimensionScale(d), y0);
        this.context.lineTo(this.xDimensionScale(d), y0 + tickSize);
      });
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.beginPath();
      this.context.moveTo(
        this.xDimensionScale(this.xmin) - hbw,
        this.computedHeight
      );
      this.context.lineTo(
        this.xDimensionScale(xmax) + 0.5 + hbw,
        this.computedHeight
      );
      this.context.strokeStyle = 'black';
      this.context.stroke();

      this.context.textAlign = 'center';
      this.context.textBaseline = 'middle';
      this.context.font = this.tick_font;
      tp.forEach(d => {
        this.context.fillText(
          d,
          this.xDimensionScale(d),
          y0 + tickSize + tickPadding * 2
        );
      });
      let caption = 'visit event';
      if (this.xaxis == 'visit_num') {
        caption = 'visit number';
      } else if (this.xaxis == 'days') {
        caption = 'time in days since first visit';
      }

      this.context.font = this.label_font;
      this.context.fillText(
        caption,
        this.computedWidth / 2,
        y0 + (tickSize + tickPadding) * 3
      );
    },
    drawAxes() {
      this.drawLeftAxis();
      this.drawRightAxis();
      this.drawBottomAxis();
    },
    updateCanvas() {
      // TODO - adding X is a workaround to account for the right-hand axis, which is outside of the computed area
      this.context.clearRect(
        0,
        0,
        this.computedWidth + this.margin.left + 100,
        this.computedHeight + this.margin.bottom + this.margin.top
      );
      if (this.cohortsHaveSubjects()) {
        this.context.translate(this.margin.left, 0);
        if (this.isCategorical) {
          this.drawCategoricalData();
        } else {
          this.drawData();
        }
        this.drawAxes();
        if (this.isCategorical) {
          this.drawCategoryColorKey();
        } else {
          this.drawCohortColorKey();
        }
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
