<template>
  <v-sheet color="white" class="rounded-lg shadow ma-0 pa-0">
    <v-container ref="bp_container" fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0" align="center" justify="center">
          <svg ref="stackedbars" :width="width" :height="height" class="mt-1">
            <g>
              <!-- bar graph rectangles -->
              <rect
                v-for="(gr, index) in graphRects"
                :key="`sbgr-${index}`"
                :ref="gr.key"
                :x="gr.x"
                :y="gr.y"
                :width="gr.w"
                :height="gr.h"
                :fill="gr.color"
                stroke="black"
              />

              <!-- x-axis at top
                  <g
                    v-xaxis="xAxis"
                    :transform="`translate(0, ${margins.top})`"
                    ></g>  -->
            </g>
          </svg>
        </v-col>
      </v-row>

      <v-row v-if="graphDataUpdated" class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <!-- tooltips for bar graph rectangles -->
          <v-tooltip
            v-for="(gr, index) in graphRects"
            :key="`sbgrtt-${index}`"
            top
            color="primary"
            :activator="gr['node']"
          >
            <span> {{ gr['label'] }} </span>
          </v-tooltip>
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
</template>

<script>
import { axisTop } from 'd3-axis';
import { format } from 'd3-format';
import { scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import { colors } from '@/utils/colors';
import 'd3-transition';

export default {
  directives: {
    xaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
    },
  },
  props: {
    height: {
      type: Number,
      required: false,
      default: 40,
    },
    width: {
      type: Number,
      required: false,
      default: 120,
    },
    rowPad: {
      type: Number,
      required: false,
      default: 4,
    },
    barPad: {
      type: Number,
      required: false,
      default: 3,
    },
    cohorts: {
      type: Array,
      required: true,
    },
    outputVar: {
      type: Object,
      required: true,
    },
    compareBy: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      colors: colors,
      container: null,
      graphData: {},
      graphDataUpdated: false,
      graphRects: [],
      graphColorKey: [],
      maxValue: null,
      maxLabelLen: 20,
      firstVisit: null,
      lastVisit: null,
    };
  },
  computed: {
    xAxis() {
      return axisTop(this.xScale);
    },
    margins() {
      return { top: 0, bottom: 0, left: 0, right: 0 };
    },
    xScale() {
      var rt = this.width - this.margins.right;
      var range = [this.margins.left, rt];
      return scaleLinear()
        .domain([0, this.maxValue])
        .range(range);
    },
  },
  watch: {
    outputVar() {
      this.updateVisits();
    },
    maxLabelLen() {
      // change in maxLabelLen means change in left margin
      this.$nextTick(() => {
        this.updateGraphData();
      });
    },
    graphData() {
      var vm = this;
      var nodesFound = true;
      this.$nextTick(() => {
        vm.graphRects.forEach(gr => {
          var node = vm.$refs[gr.key];
          if (node == null) {
            nodesFound = false;
          } else {
            gr.node = node[0];
          }
        });
        if (nodesFound) {
          vm.graphDataUpdated = true;
        }
      });
    },
    cohorts() {
      this.$nextTick(() => {
        this.updateGraphData();
      });
    },
  },
  mounted() {
    this.graphDataUpdated = false;
    this.container = this.$refs.bp_container;
    this.updateVisits();
  },
  methods: {
    onResize() {
      this.$nextTick(() => {
        this.updateGraphData();
      });
    },
    updateVisits() {
      if (this.outputVar == null) return;
      this.$nextTick(() => {
        this.updateGraphData();
      });
    },
    updateMaxLabelLen() {
      var mll = 20;
      Object.keys(this.graphData).forEach(k => {
        var ll = this.graphData[k].label.length;
        if (ll > mll) {
          mll = ll;
        }
      });

      // never use more than half the available space for labels
      var labelWidth = mll * this.labelPxPerChar;
      if (this.width > 0 && labelWidth > this.width / 2) {
        mll = Math.floor(this.width / 2 / this.labelPxPerChar);
      }
      this.maxLabelLen = mll;
    },

    // visit = firstVisit or lastVisit
    updateGraphData_aux(
      initial_y_offset,
      row_height,
      row2row_dist,
      label_prefix,
      getBarColor,
      graphData,
      graphRects
    ) {
      var vm = this;
      var x_offset = this.margins.left;
      var y_offset = initial_y_offset;
      var max_ll = this.maxLabelLen;

      const m2f = {
        'First Visit': 'firstVisit',
        'Last Visit': 'lastVisit',
        Change: 'change',
        'Rate of Change': 'roc',
      };
      const af = this.outputVar.is_longitudinal ? m2f[this.compareBy] : 'value';

      var ccounts = {};
      var ctotals = {};

      // update counts, maxValue
      this.cohorts.forEach(c => {
        var counts = {};
        var total = 0;

        c.data.forEach(x => {
          var xv = x[this.outputVar.id][af];
          if (xv != null) {
            if (!(xv in counts)) {
              counts[xv] = 0;
            }
            counts[xv] += 1;
            total += 1;
          }
        });
        if (vm.maxValue == null || total > vm.maxValue) {
          vm.maxValue = total;
        }

        ccounts[c.label] = counts;
        ctotals[c.label] = total;
      });

      var xScale = this.xScale;

      this.cohorts.forEach(c => {
        var counts = ccounts[c.label];
        var total = ctotals[c.label];
        var box_h = row_height;
        var gkey = c.label + '-' + af;

        var shortLabelFn = function(label) {
          if (label.length > max_ll) {
            return label.substr(0, max_ll - 3) + '...';
          }
          return label;
        };

        var ccount = 0;
        var rnum = 1;

        Object.keys(counts)
          .sort((x, y) => {
            return x.localeCompare(y);
          })
          .forEach(category => {
            var count = counts[category];

            var pct = (count / total) * 100.0;
            var x1 = xScale(ccount);
            var x2 = xScale(ccount + count);
            var w = x2 - x1;
            var color = getBarColor(category);
            var key = c.label + '-' + this.compareBy + '-' + rnum;
            var label =
              c.label +
              ': ' +
              category +
              ' - ' +
              count +
              ' subject(s) [' +
              format('.1f')(pct) +
              '%]';

            graphRects.push({
              x: x1,
              y: y_offset,
              w: w,
              h: row_height,
              color: color,
              key: key,
              node: null,
              label: label,
            });
            ccount += count;
            rnum++;
          });

        graphData[gkey] = {
          label: label_prefix + c.label,
          short_label: shortLabelFn(label_prefix + c.label),
          node: null,
          color: c.color,
          x: x_offset,
          y: y_offset,
          y1: y_offset,
          y2: y_offset,
          y_center: y_offset + box_h / 2,
          box_h: box_h,
        };
        y_offset += row2row_dist;
      });
    },

    updateGraphData() {
      if (!this.outputVar) return;

      this.graphData = {};
      var gData = {};

      this.graphRects = [];
      var gRects = [];

      this.graphColorKey = [];
      var rowHeight =
        (this.height - this.margins.top - this.margins.bottom) /
        this.cohorts.length;

      // create stable assignment of bar graph categories to colors
      var vm = this;
      var cindex = 0;
      var ncolors = this.colors['bar_graphs'].length;
      var cat2color = {};
      var ck_xoffset = 20;
      var getBarColor = function(category) {
        // assign color to new category, add entry to color key
        if (!(category in cat2color)) {
          cat2color[category] = vm.colors['bar_graphs'][cindex % ncolors];
          cindex++;
          vm.graphColorKey.push({
            label: category,
            color: cat2color[category],
            x: ck_xoffset,
            y: 20,
          });
          ck_xoffset += category.length * 15;
        }
        return cat2color[category];
      };

      var hrp = this.rowPad / 2.0;
      var hbp = this.barPad / 2.0;

      this.updateGraphData_aux(
        this.margins.top + hrp,
        rowHeight - hrp - hbp,
        rowHeight,
        '',
        getBarColor,
        gData,
        gRects
      );
      this.graphData = gData;
      this.graphRects = gRects;
      this.updateMaxLabelLen();
    },
  },
};
</script>

<style lang="scss" scoped></style>
