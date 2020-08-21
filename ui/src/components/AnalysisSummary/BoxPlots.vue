<template>
  <v-sheet color="white" class="rounded-lg shadow">
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-container fluid fill-width class="ma-0 pa-0">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-card color="#eeeeee" class="pt-1">
                  <v-card-title class="primary--text pl-3 py-2"
                    >Selected Cohort Boxplots
                  </v-card-title>

                  <v-card-title class="primary--text pa-0 pl-3">
                    <v-tooltip
                      v-if="selectedOutcomeVariable"
                      bottom
                      color="primary"
                    >
                      <template v-slot:activator="{ on: tooltip }">
                        <img
                          :src="
                            '/images/' +
                              selectedOutcomeVariable.category +
                              '-icon-128.png'
                          "
                          :title="selectedOutcomeVariable.category"
                          style="height:1.75em"
                          class="ma-1"
                          v-on="{ ...tooltip }"
                        />
                      </template>
                      <span>{{ selectedOutcomeVariable.category }}</span>
                    </v-tooltip>
                    <span v-if="selectedOutcomeVariable" class="subtitle-1">
                      {{ selectedOutcomeVariable.label }}
                    </span>
                  </v-card-title>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-container>

    <v-sheet color="white" class="my-3 rounded-lg shadow">
      <v-container
        ref="bp_container"
        v-resize="onResize"
        fluid
        fill-width
        class="ma-0 pa-0"
      >
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <svg ref="boxplots" :width="width" :height="height">
              <g
                v-if="
                  selectedOutcomeVariable &&
                    selectedOutcomeVariable.data_category != 'Categorical'
                "
              >
                <!-- labels -->
                <text
                  v-for="sc in Object.keys(boxplotStats)"
                  :x="15"
                  :y="boxplotStats[sc]['y_center']"
                >
                  {{ boxplotStats[sc].label }}
                </text>

                <!-- endcap lines -->
                <line
                  v-for="sc in Object.keys(boxplotStats)"
                  :x1="boxplotStats[sc]['min_x']"
                  :x2="boxplotStats[sc]['min_x']"
                  :y1="boxplotStats[sc]['y1']"
                  :y2="boxplotStats[sc]['y2']"
                  stroke="black"
                />

                <line
                  v-for="sc in Object.keys(boxplotStats)"
                  :x1="boxplotStats[sc]['max_x']"
                  :x2="boxplotStats[sc]['max_x']"
                  :y1="boxplotStats[sc]['y1']"
                  :y2="boxplotStats[sc]['y2']"
                  stroke="black"
                />

                <!-- center line -->
                <line
                  v-for="sc in Object.keys(boxplotStats)"
                  :x1="boxplotStats[sc]['min_x']"
                  :x2="boxplotStats[sc]['max_x']"
                  :y1="boxplotStats[sc]['y_center']"
                  :y2="boxplotStats[sc]['y_center']"
                  stroke="black"
                />

                <!-- box -->
                <rect
                  v-for="sc in Object.keys(boxplotStats)"
                  :x="boxplotStats[sc]['q1_x']"
                  :y="boxplotStats[sc]['y1']"
                  :width="boxplotStats[sc]['q1_q3_w']"
                  :height="boxplotStats[sc]['box_h']"
                  :fill="boxplotStats[sc]['color']"
                  stroke="black"
                />

                <!-- median line -->
                <line
                  v-for="sc in Object.keys(boxplotStats)"
                  :x1="boxplotStats[sc]['median_x']"
                  :x2="boxplotStats[sc]['median_x']"
                  :y1="boxplotStats[sc]['y1']"
                  :y2="boxplotStats[sc]['y2']"
                  stroke="black"
                  stroke-width="2"
                />

                <!-- x-axis at top -->
                <g
                  v-xaxis="xAxis"
                  :transform="`translate(0, ${margins.top})`"
                ></g>
              </g>
            </svg>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/analysisSummary/types';
import { state as deState } from '@/store/modules/dataExplorer/types';
import { min, max, ascending, quantile } from 'd3-array';
import { axisTop, axisLeft, axisRight } from 'd3-axis';
import { format } from 'd3-format';
import { scaleLinear } from 'd3-scale';
import { select, event } from 'd3-selection';
import { colors } from '@/utils/colors';
import 'd3-transition';

export default {
  components: {},
  directives: {
    xaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
    },
  },
  props: {
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
      colors: colors,
      container: null,
      width: 0,
      height: 0,
      boxplotStats: {},
      margins: { top: 40, bottom: 40, left: 250, right: 20 },
      rowHeight: 100,
      rowPad: 15,
      maxValue: null,
      firstVisit: null,
      lastVisit: null,
    };
  },
  computed: {
    ...mapState('analysisSummary', {
      selectedCohorts: state.SELECTED_COHORTS,
      selectedOutcomeVariable: state.SELECTED_OUTCOME_VARIABLE,
    }),
    ...mapState('dataExplorer', {
      collection: deState.COLLECTION,
      data: deState.DATA,
      outcomeVariables: deState.OUTCOME_VARIABLES,
    }),
    xAxis() {
      return axisTop(this.xScale);
    },
    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;
      let ccnum = 0;

      this.selectedCohorts.forEach(e => {
        if (e.collection_id === cid) {
          e.index = ccnum;
          ccnum += 1;
          cch.push(e);
        }
      });

      return cch;
    },
    xScale() {
      var rt = this.width - this.margins.right;

      // take flip_axis into account:
      //      var range =
      //        this.selectedOutcomeVariable && this.selectedOutcomeVariable.flip_axis
      //          ? [rt, this.margins.left]
      //          : [this.margins.left, rt];

      // or not:
      var range = [this.margins.left, rt];
      return scaleLinear()
        .domain([0, this.maxValue])
        .range(range);
    },
  },
  watch: {
    selectedOutcomeVariable(ov) {
      // update first/last visit
      var bp = this;
      this.collection.observation_variables_list.forEach(v => {
        if (v.ontology.id == ov.id) {
          bp.firstVisit = v.first_visit_event;
          bp.lastVisit = v.last_visit_event;
        }
      });

      this.$nextTick(() => {
        this.updateStats();
      });
    },
  },
  created() {},
  mounted() {
    this.container = this.$refs.bp_container;
    this.resizeChart();
    this.updateStats();
  },
  methods: {
    onResize() {
      this.$nextTick(() => {
        this.resizeChart();
        this.updateStats();
      });
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

      // compute height based on rowHeight
      height =
        this.rowHeight * this.selectedCohorts.length +
        this.margins.top +
        this.margins.bottom;

      //      console.log(
      //        'resizeChart() setting this.height = ' +
      //          height +
      //          ' this.width = ' +
      //          width
      //      );
      this.height = height;
      this.width = width;
    },
    // visit = firstVisit or lastVisit
    updateStats_aux(
      visit,
      y_offset,
      pad_top,
      pad_bottom,
      row_height,
      row2row_dist,
      label_suffix
    ) {
      // compute boxplot stats for each cohort
      var x_offset = this.margins.left;

      this.selectedCohorts.forEach(c => {
        const subjids = [];
        c.subject_ids.forEach(sid => {
          subjids[sid] = 1;
        });
        const cohortData = this.data
          .filter(d => d.subject_id in subjids)
          .map(x => x[this.selectedOutcomeVariable.id][visit])
          .sort(ascending);

        const cmin = min(cohortData);
        const cmax = max(cohortData);

        var q1 = quantile(cohortData, 0.25);
        var median = quantile(cohortData, 0.5);
        var q3 = quantile(cohortData, 0.75);
        var interQuantileRange = q3 - q1;
        var boxMin = q1 - 1.5 * interQuantileRange;
        var boxMax = q3 + 1.5 * interQuantileRange;

        //        console.log('cmin=' +
        //          cmin +
        //          ' cmax=' +
        //          cmax +
        //         ' median=' + median +
        //         ' scale(cmin)=' +
        //         this.xScale(cmin) +
        //         ' scale(cmax)=' +
        //         this.xScale(cmax) + " boxMin=" + boxMin + " boxMax=" + boxMax
        //        );

        var box_h = row_height - (pad_top + pad_bottom);

        this.boxplotStats[c.id + '-' + visit] = {
          label: c.label + label_suffix,
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
      if (!this.selectedOutcomeVariable) return;

      this.boxplotStats = {};

      // overall max value
      var accFn = x => x[this.selectedOutcomeVariable.id];
      var allData = this.data.map(x => accFn(x));
      const firstMax = max(allData, d => d.firstVisit);
      const lastMax = max(allData, d => d.lastVisit);
      this.maxValue = Math.max(firstMax, lastMax);

      var hrh = this.rowHeight / 2.0;

      this.updateStats_aux(
        'firstVisit',
        this.margins.top,
        15,
        5,
        hrh,
        this.rowHeight,
        ' | ' + this.firstVisit
      );
      this.updateStats_aux(
        'lastVisit',
        this.margins.top + hrh,
        5,
        15,
        hrh,
        this.rowHeight,
        ' | ' + this.lastVisit
      );
    },
  },
};
</script>

<style lang="scss" scoped></style>
