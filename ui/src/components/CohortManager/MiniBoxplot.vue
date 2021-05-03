<template>
  <v-tooltip bottom color="primary">
    <template v-slot:activator="{ on: tooltip }">
      <v-sheet
        color="white"
        class="rounded-lg shadow ma-0 pa-0"
        v-on="{ ...tooltip }"
      >
        <v-container ref="bp_container" fluid fill-width class="ma-0 pa-0">
          <v-row class="ma-0 pa-0">
            <v-col cols="12" class="ma-0 pa-0" align="center" justify="center">
              <svg ref="boxplots" :width="width" :height="height" class="mt-1">
                <g>
                  <!-- endcap lines -->
                  <line
                    v-for="(sc, index) in Object.keys(boxplotStats)"
                    :key="`s-el1-${index}`"
                    :x1="boxplotStats[sc]['min_x']"
                    :x2="boxplotStats[sc]['min_x']"
                    :y1="boxplotStats[sc]['y1']"
                    :y2="boxplotStats[sc]['y2']"
                    stroke="black"
                  />

                  <line
                    v-for="(sc, index) in Object.keys(boxplotStats)"
                    :key="`s-el2-${index}`"
                    :x1="boxplotStats[sc]['max_x']"
                    :x2="boxplotStats[sc]['max_x']"
                    :y1="boxplotStats[sc]['y1']"
                    :y2="boxplotStats[sc]['y2']"
                    stroke="black"
                  />

                  <!-- center line -->
                  <line
                    v-for="(sc, index) in Object.keys(boxplotStats)"
                    :key="`s-cl-${index}`"
                    :x1="boxplotStats[sc]['min_x']"
                    :x2="boxplotStats[sc]['max_x']"
                    :y1="boxplotStats[sc]['y_center']"
                    :y2="boxplotStats[sc]['y_center']"
                    stroke="black"
                  />

                  <!-- box -->
                  <rect
                    v-for="(sc, index) in Object.keys(boxplotStats)"
                    :key="`s-b-${index}`"
                    :x="
                      axisFlipped
                        ? boxplotStats[sc]['q3_x']
                        : boxplotStats[sc]['q1_x']
                    "
                    :y="boxplotStats[sc]['y1']"
                    :width="boxplotStats[sc]['q1_q3_w']"
                    :height="boxplotStats[sc]['box_h']"
                    :fill="boxplotStats[sc]['color']"
                    stroke="none"
                    stroke-width="0.5"
                  />

                  <!-- median line -->
                  <line
                    v-for="(sc, index) in Object.keys(boxplotStats)"
                    :key="`s-ml-${index}`"
                    :x1="boxplotStats[sc]['median_x']"
                    :x2="boxplotStats[sc]['median_x']"
                    :y1="boxplotStats[sc]['y1']"
                    :y2="boxplotStats[sc]['y2']"
                    stroke="black"
                    stroke-width="2"
                  />

                  <!-- x-axis at top -->
                  <!--
              <g
                v-xaxis="xAxis"
		:transform="`translate(0, ${margins.top})`"
                ></g> -->
                </g>
              </svg>
            </v-col>
          </v-row>
        </v-container>
      </v-sheet>
    </template>
    <span class="subtitle-1">
      {{
        outputVar.label +
          (axisFlipped ? ' ' + maxValue + ' - 0' : ' 0 - ' + maxValue)
      }}
    </span>
  </v-tooltip>
</template>

<script>
import { min, max, ascending, quantile } from 'd3-array';
import { axisTop } from 'd3-axis';
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
    doFlipAxis: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  data() {
    return {
      colors: colors,
      boxplotStats: {},
      boxplotStatsUpdated: false,
      maxValue: null,
    };
  },
  computed: {
    xAxis() {
      return axisTop(this.xScale);
    },
    axisFlipped() {
      return this.outcomeVar && this.outcomeVar.flip_axis;
    },
    xScale() {
      var range = null;
      if (this.doFlipAxis) {
        range = this.axisFlipped ? [this.width, 0] : [0, this.width];
      } else {
        range = [0, this.width];
      }
      return scaleLinear()
        .domain([0, this.maxValue])
        .range(range);
    },
  },
  watch: {
    boxplotStats(bps) {
      var vm = this;
      var nodesFound = true;
      this.$nextTick(() => {
        Object.keys(bps).forEach(k => {
          var node = vm.$refs[k];
          if (node == null) {
            nodesFound = false;
          } else {
            bps[k].node = node[0];
          }
        });
        if (nodesFound) {
          vm.boxplotStatsUpdated = true;
        }
      });
    },
  },
  created() {
    this.updateStats();
  },
  mounted() {
    this.boxplotStatsUpdated = false;
  },
  methods: {
    // visit = firstVisit or lastVisit
    updateStats_aux(
      visit,
      initial_y_offset,
      pad_top,
      pad_bottom,
      row_height,
      row2row_dist,
      stats
    ) {
      // compute boxplot stats for each cohort
      var x_offset = 0;
      var y_offset = initial_y_offset;
      var cnum = 1;

      this.cohorts.forEach(c => {
        const cohortData = c.data
          .map(x => x[this.outputVar.id][visit])
          .sort(ascending);

        const cmin = min(cohortData);
        const cmax = max(cohortData);

        var q1 = quantile(cohortData, 0.25);
        var median = quantile(cohortData, 0.5);
        var q3 = quantile(cohortData, 0.75);
        var interQuantileRange = q3 - q1;
        var boxMin = q1 - 1.5 * interQuantileRange;
        var boxMax = q3 + 1.5 * interQuantileRange;

        var box_h = row_height - (pad_top + pad_bottom);
        var bpKey = cnum + '' + visit;
        ++cnum;

        stats[bpKey] = {
          node: null,
          color: c.color,
          x: x_offset,
          y: y_offset,
          y1: y_offset + pad_top,
          y2: y_offset + row_height - pad_bottom,
          y_center: y_offset + pad_top + box_h / 2.0,
          min: cmin,
          max: cmax,
          min_x: this.xScale(cmin),
          max_x: this.xScale(cmax),
          max_min_w: Math.abs(this.xScale(cmax) - this.xScale(cmin)),
          q1_x: this.xScale(q1),
          median_x: this.xScale(median),
          q3_x: this.xScale(q3),
          q1_q3_w: Math.abs(this.xScale(q3) - this.xScale(q1)),
          boxmin_x: this.xScale(boxMin),
          boxmax_x: this.xScale(boxMax),
          box_w: Math.abs(this.xScale(boxMax) - this.xScale(boxMin)),
          box_h: box_h,
        };
        y_offset += row2row_dist;
      });
    },
    updateStats() {
      this.boxplotStats = {};
      var bpStats = {};

      const m2f = {
        'First Visit': 'firstVisit',
        'Last Visit': 'lastVisit',
        Change: 'change',
        'Rate of Change': 'roc',
      };
      const af = m2f[this.compareBy];
      var maxval = null;

      // overall max value
      var accFn = x => x[this.outputVar.id];
      this.cohorts.forEach(c => {
        const cmax = max(c.data, d => accFn(d)[af]);
        if (maxval == null || cmax > maxval) {
          maxval = cmax;
        }
      });

      this.maxValue = maxval;
      var rowHeight = this.height / this.cohorts.length;
      this.updateStats_aux(af, 0, 2, 2, rowHeight, rowHeight, bpStats);
      this.boxplotStats = bpStats;
    },
  },
};
</script>

<style lang="scss" scoped></style>
