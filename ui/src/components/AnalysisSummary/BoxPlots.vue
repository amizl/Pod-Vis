><template>
  <v-sheet color="white" class="rounded-lg shadow">
    <v-container v-if="showTitleBar" fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-container fluid fill-width class="ma-0 pa-0">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-card color="#eeeeee" class="pt-1">
                  <v-card-title class="primary--text pl-3 py-2"
                    >Selected Cohorts - Boxplots
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

                  <v-tooltip v-if="outcomeVar" top color="primary">
                    <template v-slot:activator="{ on: tooltip }">
                      <span v-on="{ ...tooltip }">
                        {{ outcomeVar.abbreviation }}
                      </span>
                    </template>
                    <span v-html="outcomeVar.label"></span>
                  </v-tooltip>
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

            <svg v-else ref="boxplots" :width="width" :height="height">
              <g v-if="outcomeVar && outcomeVar.data_category != 'Categorical'">
                <!-- labels -->
                <text
                  v-for="(sc, index) in Object.keys(boxplotStats)"
                  :key="`s-lbl-${index}`"
                  :ref="sc"
                  :x="15"
                  :y="boxplotStats[sc]['y_center'] + rowPad / 2"
                >
                  {{ boxplotStats[sc].short_label }}
                </text>

                <!-- endcap lines -->
                <line
                  v-for="(sc, index) in Object.keys(boxplotStats)"
                  :key="`s-ecl-${index}`"
                  :x1="boxplotStats[sc]['min_x']"
                  :x2="boxplotStats[sc]['min_x']"
                  :y1="boxplotStats[sc]['y1']"
                  :y2="boxplotStats[sc]['y2']"
                  stroke="black"
                />

                <line
                  v-for="(sc, index) in Object.keys(boxplotStats)"
                  :key="`s-l-${index}`"
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
                  stroke="black"
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
                  stroke-width="3"
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

        <!-- tooltips for cohort + visit labels -->
        <v-row v-if="boxplotStatsUpdated" class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-tooltip
              v-for="(sc, index) in Object.keys(boxplotStats)"
              :key="`s-tt-${index}`"
              top
              color="primary"
              :activator="boxplotStats[sc]['node']"
            >
              <span> {{ boxplotStats[sc]['label'] }} </span>
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
import { min, max, ascending, quantile } from 'd3-array';
import { axisTop } from 'd3-axis';
import { scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
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
      required: true,
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
    doFlipAxis: {
      type: Boolean,
      required: false,
      default: true,
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
      boxplotStats: {},
      boxplotStatsUpdated: false,
      minValue: null,
      maxValue: null,
      firstVisit: null,
      lastVisit: null,
      maxLabelLen: null,
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
      return { top: 40, bottom: 40, left: leftMargin, right: 20 };
    },
    axisFlipped() {
      return this.outcomeVar && this.outcomeVar.flip_axis;
    },
    xScale() {
      var rt = this.width - this.margins.right;
      var range = null;

      // take flip_axis into account:
      if (this.doFlipAxis) {
        range = this.axisFlipped
          ? [rt, this.margins.left]
          : [this.margins.left, rt];
      }
      // or don't:
      else {
        range = [this.margins.left, rt];
      }
      return scaleLinear()
        .domain([this.minValue, this.maxValue])
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
        this.updateStats();
        this.resizeChart();
      });
    },
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
    cohorts() {
      this.resizeChart();
      this.updateVisits();
    },
  },
  mounted() {
    this.boxplotStatsUpdated = false;
    this.container = this.$refs.bp_container;
    this.resizeChart();
    this.updateVisits();
  },
  methods: {
    onResize() {
      this.$nextTick(() => {
        this.resizeChart();
        this.updateStats();
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
        this.updateStats();
      });
    },
    updateMaxLabelLen() {
      var mll = 20;
      Object.keys(this.boxplotStats).forEach(k => {
        var ll = this.boxplotStats[k].label.length;
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
    updateStats_aux(
      visit,
      initial_y_offset,
      row_height,
      row2row_dist,
      label_prefix,
      stats
    ) {
      // compute boxplot stats for each cohort
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
          .map(x => x[this.outcomeVar.id][visit])
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

        var box_h = row_height;
        var bpKey = c.id + '' + visit;
        var shortLabelFn = function(label) {
          if (label.length > max_ll) {
            return label.substr(0, max_ll - 3) + '...';
          }
          return label;
        };

        stats[bpKey] = {
          label: label_prefix + c.label,
          short_label: shortLabelFn(label_prefix + c.label),
          node: null,
          color: c.color,
          x: x_offset,
          y: y_offset,
          y1: y_offset,
          y2: y_offset + row_height,
          y_center: y_offset + box_h / 2.0,
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
      if (!this.outcomeVar) return;

      this.boxplotStats = {};
      var bpStats = {};

      // overall min, max value
      var accFn = x => x[this.outcomeVar.id];
      var allData = this.data.map(x => accFn(x));
      if (this.outcomeVar.is_longitudinal) {
        const firstMin = min(allData, d => d.firstVisit);
        const lastMin = min(allData, d => d.lastVisit);
        this.minValue = Math.min(firstMin, lastMin);
        const firstMax = max(allData, d => d.firstVisit);
        const lastMax = max(allData, d => d.lastVisit);
        this.maxValue = Math.max(firstMax, lastMax);
      } else {
        this.minValue = min(allData, d => d.value);
        this.maxValue = max(allData, d => d.value);
      }

      var hrh = this.rowHeight / 2.0;
      var hrp = this.rowPad / 2.0;
      var hbp = this.barPad / 2.0;

      if (this.outcomeVar.is_longitudinal) {
        this.updateStats_aux(
          'firstVisit',
          this.margins.top + hrp,
          hrh - hrp - hbp,
          this.rowHeight,
          this.firstVisit + ' | ',
          bpStats
        );
        this.updateStats_aux(
          'lastVisit',
          this.margins.top + hrh + hbp,
          hrh - hrp - hbp,
          this.rowHeight,
          this.lastVisit + ' | ',
          bpStats
        );
      }
      // cross-sectional data
      else {
        this.updateStats_aux(
          'value',
          this.margins.top + hbp + hrh / 4,
          this.rowHeight - hrp - hbp,
          this.rowHeight,
          '',
          bpStats
        );
      }
      this.boxplotStats = bpStats;
      this.updateMaxLabelLen();
    },
  },
};
</script>

<style lang="scss" scoped></style>
