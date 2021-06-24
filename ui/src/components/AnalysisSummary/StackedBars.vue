<template>
  <v-sheet color="white" class="rounded-lg shadow">
    <v-container v-if="showTitleBar" fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-container fluid fill-width class="ma-0 pa-0">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-card color="#eeeeee" class="pt-1">
                  <v-card-title class="primary--text pl-3 py-2"
                    >Selected Cohorts - Bar Charts
                  </v-card-title>

                  <v-card-title class="primary--text pa-0 pl-3">
                    <v-tooltip v-if="outcomeVar" bottom color="primary">
                      <template v-slot:activator="{ on: tooltip }">
                        <img
                          :src="
                            '/images/' + outcomeVar.category + '-icon-128.png'
                          "
                          :title="outcomeVar.category"
                          style="height:1.75em"
                          class="ma-1"
                          v-on="{ ...tooltip }"
                        />
                      </template>
                      <span>{{ outcomeVar.category }}</span>
                    </v-tooltip>
                    <span v-if="outcomeVar" class="subtitle-1">
                      {{ outcomeVar.label }}
                    </span>
                  </v-card-title>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-container>

    <v-container v-else fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-container fluid fill-width class="ma-0 pa-0">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-card-title class="primary--text pa-0 pt-3 pl-2">
                  <v-tooltip v-if="outcomeVar" bottom color="primary">
                    <template v-slot:activator="{ on: tooltip }">
                      <img
                        :src="
                          '/images/' + outcomeVar.category + '-icon-128.png'
                        "
                        :title="outcomeVar.category"
                        style="height:1.75em"
                        class="ma-1"
                        v-on="{ ...tooltip }"
                      />
                    </template>
                    <span>{{ outcomeVar.category }}</span>
                  </v-tooltip>
                  <span v-if="outcomeVar" class="subtitle-1">
                    {{ outcomeVar.label }}
                  </span>
                </v-card-title>
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
            <div
              v-if="!outcomeVar"
              column
              align-center
              justify-center
              fill-width
            >
              <v-subheader class="title primary--text text--lighten-5">
                NO VARIABLE SELECTED
              </v-subheader>
            </div>

            <div
              v-else-if="!cohorts || cohorts.length == 0"
              class="display-1 primary--text text--lighten-5 pt-5 mt-5"
              align="center"
            >
              NO COHORTS SELECTED
            </div>

            <svg v-else ref="stackedbars" :width="width" :height="height">
              <g v-if="outcomeVar && outcomeVar.data_category == 'Categorical'">
                <!-- labels -->
                <text
                  v-for="(sc, index) in Object.keys(graphData)"
                  :key="`st-${index}`"
                  :ref="sc"
                  :x="15"
                  :y="graphData[sc]['y_center']"
                >
                  {{ graphData[sc].short_label }}
                </text>

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

                <!-- color key -->
                <rect
                  v-for="(gc, index) in graphColorKey"
                  :key="`sck-${index}`"
                  :x="gc.x"
                  :y="gc.y"
                  :width="20"
                  :height="20"
                  :fill="gc.color"
                  stroke="black"
                />
                <!-- labels -->
                <text
                  v-for="(gc, index) in graphColorKey"
                  :key="`sl-${index}`"
                  :x="gc.x + 35"
                  :y="gc.y + 15"
                >
                  {{ gc.label }}
                </text>

                <!-- x-axis at top -->
                <g
                  v-xaxis="xAxis"
                  :transform="`translate(0, ${margins.top})`"
                ></g>
              </g>
            </svg>
          </v-col>
        </v-row>

        <v-row v-if="graphDataUpdated" class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <!-- tooltips for cohort + visit labels -->
            <v-tooltip
              v-for="(sc, index) in Object.keys(graphData)"
              :key="`sltt-${index}`"
              top
              color="primary"
              :activator="graphData[sc]['node']"
            >
              <span> {{ graphData[sc]['label'] }} </span>
            </v-tooltip>

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
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state as deState } from '@/store/modules/dataExplorer/types';
import { axisTop } from 'd3-axis';
import { format } from 'd3-format';
import { scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import { colors } from '@/utils/colors';
import { getLabelWidth } from '@/utils/helpers';
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
    showTitleBar: {
      type: Boolean,
      required: false,
      default: true,
    },
    cohorts: {
      type: Array,
      required: true,
      default: () => [],
    },
    outcomeVar: {
      type: Object,
      default: null,
    },
    minHeight: {
      type: Number,
      required: false,
      default: 400,
    },
    minWidth: {
      type: Number,
      required: false,
      default: 300,
    },
    labelPxPerChar: {
      type: Number,
      required: false,
      default: 10,
    },
    maxCohorts: {
      type: Number,
      required: false,
      default: 1,
    },
    rowHeight: {
      type: Number,
      required: false,
      default: 100,
    },
    rowPad: {
      type: Number,
      required: false,
      default: 12,
    },
    barPad: {
      type: Number,
      required: false,
      default: 5,
    },
  },
  data() {
    return {
      colors: colors,
      container: null,
      width: 0,
      height: 0,
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
    ...mapState('dataExplorer', {
      collection: deState.COLLECTION,
      data: deState.DATA,
      outcomeVariables: deState.OUTCOME_VARIABLES,
    }),
    xAxis() {
      return axisTop(this.xScale);
    },
    margins() {
      var leftMargin = this.maxLabelLen * this.labelPxPerChar;
      return { top: 20, bottom: 150, left: leftMargin, right: 20 };
    },
    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;
      let ccnum = 0;

      this.cohorts.forEach(e => {
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
      var range = [this.margins.left, rt];
      return scaleLinear()
        .domain([0, this.maxValue])
        .range(range);
    },
  },
  watch: {
    outcomeVar() {
      this.updateVisits();
    },
    maxLabelLen() {
      // change in maxLabelLen means change in left margin
      this.$nextTick(() => {
        this.updateGraphData();
        this.resizeChart();
      });
    },
    graphData(gd) {
      var vm = this;
      var nodesFound = true;
      this.$nextTick(() => {
        Object.keys(gd).forEach(k => {
          var node = vm.$refs[k];
          if (node == null) {
            nodesFound = false;
          } else {
            gd[k].node = node[0];
          }
        });
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
        this.resizeChart();
        this.updateGraphData();
      });
    },
  },
  mounted() {
    this.graphDataUpdated = false;
    this.container = this.$refs.bp_container;
    this.resizeChart();
    this.updateVisits();
  },
  methods: {
    onResize() {
      this.$nextTick(() => {
        this.resizeChart();
        this.updateGraphData();
      });
    },
    updateVisits() {
      var bp = this;
      if (this.outcomeVar == null) return;
      this.collection.observation_variables_list.forEach(v => {
        if (v.ontology.id == bp.outcomeVar.id) {
          if (v.first_visit_event != null) {
            bp.firstVisit = v.first_visit_event;
            bp.lastVisit = v.last_visit_event;
          } else if (v.first_visit_num != null) {
            bp.firstVisit = v.first_visit_num;
            bp.lastVisit = v.last_visit_num;
          }
        }
      });
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
    resizeChart() {
      if (this.container == null) {
        return;
      }
      var { width, height } = this.container.getBoundingClientRect();
      //      console.log("resizeChart() client height = " + height + " width = " + width);

      // establish minimum height
      if (height < this.minHeight) {
        height = this.minHeight;
      }
      if (width < this.minWidth) {
        width = this.minWidth;
      }

      // compute height based on rowHeight
      var nCohorts = this.cohorts.length;
      if (this.maxCohorts && this.maxCohorts > nCohorts)
        nCohorts = this.maxCohorts;
      height =
        this.rowHeight * nCohorts + this.margins.top + this.margins.bottom;

      this.height = height;
      this.width = width;
    },

    // visit = firstVisit or lastVisit
    updateGraphData_aux(
      visit,
      initial_y_offset,
      row_height,
      row2row_dist,
      label_prefix,
      getBarColor,
      graphData,
      graphRects
    ) {
      var vm = this;
      var xScale = this.xScale;
      var x_offset = this.margins.left;
      var y_offset = initial_y_offset;
      var max_ll = this.maxLabelLen;
      this.cohorts.forEach(c => {
        const subjids = [];
        c.subject_ids.forEach(sid => {
          subjids[sid] = 1;
        });

        const cohortData = this.data
          .filter(d => d.subject_id in subjids)
          .map(x => x[this.outcomeVar.id][visit]);
        var counts = {};
        var total = 0;
        cohortData.forEach(x => {
          if (x != null) {
            if (!(x in counts)) {
              counts[x] = 0;
            }
            counts[x] += 1;
            total += 1;
          }
        });
        if (vm.maxValue == null || total > vm.maxValue) {
          vm.maxValue = total;
        }

        var box_h = row_height;
        var gkey = c.id + '-' + visit;

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
            var key = c.id + '-' + visit + '-' + rnum;
            var label =
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
      if (!this.outcomeVar) return;

      this.graphData = {};
      var gData = {};

      this.graphRects = [];
      var gRects = [];

      this.graphColorKey = [];
      var hrh = this.rowHeight / 2.0;

      // create stable assignment of bar graph categories to colors
      var vm = this;
      var cindex = 0;
      var ncolors = this.colors['bar_graphs'].length;
      var cat2color = {};
      var ck_xoffset = 20;
      var ck_yoffset = vm.height - 110;
      var getBarColor = function(category) {
        // assign color to new category, add entry to color key
        if (!(category in cat2color)) {
          cat2color[category] = vm.colors['bar_graphs'][cindex % ncolors];
          cindex++;
          vm.graphColorKey.push({
            label: category,
            color: cat2color[category],
            x: ck_xoffset,
            y: ck_yoffset,
          });

          // new line guesstimate
          var label_width = getLabelWidth(category);

          if (ck_xoffset + label_width > vm.width - vm.margins.right - 20) {
            ck_xoffset = 20;
            ck_yoffset += 35;
          } else {
            ck_xoffset += label_width;
          }
        }
        return cat2color[category];
      };

      var hrp = this.rowPad / 2.0;
      var hbp = this.barPad / 2.0;

      if (this.outcomeVar.is_longitudinal) {
        this.updateGraphData_aux(
          'firstVisit',
          this.margins.top + hrp,
          hrh - hrp - hbp,
          this.rowHeight,
          this.firstVisit + ' | ',
          getBarColor,
          gData,
          gRects
        );
        this.updateGraphData_aux(
          'lastVisit',
          this.margins.top + hrh + hbp,
          hrh - hrp - hbp,
          this.rowHeight,
          this.lastVisit + ' | ',
          getBarColor,
          gData,
          gRects
        );
      }
      // cross-sectional data
      else {
        this.updateGraphData_aux(
          'value',
          this.margins.top + hbp + hrh / 4,
          this.rowHeight - hrp - hbp,
          this.rowHeight,
          '',
          getBarColor,
          gData,
          gRects
        );
      }
      this.graphData = gData;
      this.graphRects = gRects;
      this.updateMaxLabelLen();
    },
  },
};
</script>

<style lang="scss" scoped></style>
