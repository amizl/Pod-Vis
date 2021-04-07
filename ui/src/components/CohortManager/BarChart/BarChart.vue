<template>
  <v-container fluid fill-width class="pa-0 ma-0">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <v-chip
          v-if="showHelpChip"
          label
          close
          color="#4caf50"
          class="font-weight-bold white--text pa-2 my-1"
          @click:close="showHelpChip = false"
          >Click on bar to toggle category inclusion OR use checkboxes
          below.</v-chip
        >

        <svg ref="chart" :width="width" :height="height">
          <g
            v-if="width && height"
            ref="bars"
            :transform="`translate(${margin.left}, ${margin.top})`"
          >
            <bar-rect
              v-for="d in populationData"
              :key="'pd' + d.key"
              :x="xScale(d.key)"
              :y="yScale(d.value)"
              :width="xScale.bandwidth()"
              :height="h - yScale(d.value) > 0 ? h - yScale(d.value) : 0"
              :fill="colors['population']"
              :tooltip="barTooltip"
              @click.native="userClickedBar(d.key)"
            />

            <bar-rect
              v-for="d in data"
              :key="'d-' + d.key"
              :x="xScale(d.key)"
              :y="yScale(d.value)"
              :width="xScale.bandwidth()"
              :height="h - yScale(d.value) > 0 ? h - yScale(d.value) : 0"
              :fill="getFill(d.key)"
              :tooltip="barTooltip"
              @click.native="userClickedBar(d.key)"
            />
          </g>
          <g
            v-xaxis="xAxis"
            :transform="`translate(${margin.left},${h + margin.top})`"
          ></g>
          <g
            v-yaxis="yAxis"
            :transform="`translate(${margin.left}, ${margin.top})`"
          ></g>
        </svg>
      </v-col>
    </v-row>

    <v-row v-if="showSelection" class="ma-0 pa-0">
      <v-col cols="12" class="center-text pa-0 ma-0">
        <v-tabs v-model="tab">
          <v-tab key="cats">Selected Categories</v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab">
          <!-- selected categories -->
          <v-tab-item key="cats">
            <v-list dense class="pa-0 ma-0 mt-2">
              <v-list-item v-for="d in sortedData" :key="d.key">
                <v-list-item-icon class="ma-0 pa-0" justify="end">
                  <v-checkbox
                    v-model="cat_cbs"
                    dense
                    hide-details
                    :label="d.key"
                    :value="d.key"
                  ></v-checkbox>
                </v-list-item-icon>
                <v-list-item-content class="pa-0 ma-0">
                  <v-list-item-title
                    align="end"
                    justify="center"
                    valign="center"
                  >
                    <v-chip
                      small
                      label
                      color="primary"
                      class="white--text title mx-2"
                      align="end"
                      justify="center"
                      >{{ d.value }}</v-chip
                    >
                  </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
// Data Store
import { mapState, mapActions, mapGetters } from 'vuex';
import { state, actions, getters } from '@/store/modules/cohortManager/types';

import {
  axisOrdinalBottom,
  axisLeft,
  axisLabelOffset,
  axisLabelRotate,
} from 'd3fc';

// D3 Modules
import { max } from 'd3-array';
import { select } from 'd3-selection';
import { scaleLinear, scaleBand, scaleOrdinal } from 'd3-scale';
import 'd3-transition';
import { schemeCategory10 } from 'd3-scale-chromatic';

import resize from 'vue-resize-directive';
import { colors } from '@/utils/colors';
import BarRect from './BarRect.vue';

const PX_PER_LABEL_LINE = 15;
const N_LABEL_LINES = 4;
// set one but not both of these to true:
const ROTATE_LABELS = false;
const OFFSET_LABELS = true;

export default {
  directives: {
    resize,
    xaxis(el, binding) {
      const axisMethod = binding.value;
      select(el).call(axisMethod);
      // .selectAll('path')
      // .attr('stroke', '#E8EAF6')
      // .attr('stroke-width', 3);
    },
    yaxis(el, binding) {
      const axisMethod = binding.value;
      select(el)
        // .transition()
        .call(axisMethod);
      // .selectAll('path')
      // .attr('stroke', '#E8EAF6')
      // .attr('stroke-width', 3);
    },
  },
  components: {
    BarRect,
  },
  props: {
    id: {
      type: [Number, String],
      required: true,
    },
    dimensionName: {
      type: String,
      required: true,
    },
    barTooltip: {
      type: String,
      required: false,
      default: '',
    },
    showSelection: {
      type: Boolean,
      required: false,
      default: false,
    },
    showFilterHelp: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      isLoading: true,
      haveDimensions: false,
      width: 0,
      height: 0,
      margin: {
        top: 10,
        right: 30,
        bottom: 20,
        left: 50,
      },
      selected: [],
      container: null,
      dimension: null,
      group: [],
      data: [],
      colors: colors,
      // current tab
      tab: 'cats',
      // category checkboxes
      cat_cbs: [],
      showHelpChip: false,
    };
  },
  computed: {
    ...mapGetters('cohortManager', {
      findCohortQuery: getters.FIND_COHORT_QUERY,
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      dimensions: state.DIMENSIONS,
      cohort: state.COHORT,
    }),
    w() {
      const { left, right } = this.margin;
      const { width } = this;
      return width - left - right;
    },
    h() {
      const { top, bottom } = this.margin;
      const { height } = this;
      return height - top - bottom - (N_LABEL_LINES - 1) * PX_PER_LABEL_LINE;
    },
    colorScale() {
      return scaleOrdinal()
        .domain(this.data.map(c => c.key))
        .range(schemeCategory10);
    },
    sortedPopulationData() {
      return [...this.populationData].sort((x, y) =>
        x.key.localeCompare(y.key)
      );
    },
    sortedData() {
      return [...this.data].sort((x, y) => x.key.localeCompare(y.key));
    },
    xScale() {
      return scaleBand()
        .domain(this.sortedPopulationData.map(d => d.key))
        .range([0, this.w])
        .padding(0.05);
    },
    yScale() {
      return scaleLinear()
        .domain([0, max(this.populationData, d => d.value)])
        .range([this.h, 0]);
    },
    xAxis() {
      var xaxis = null;
      if (ROTATE_LABELS) {
        xaxis = axisLabelRotate(axisOrdinalBottom(this.xScale));
        if (this.populationData.map(d => d.key).length > 2) {
          xaxis.labelRotate(18);
        }
      } else if (OFFSET_LABELS) {
        xaxis = axisLabelOffset(axisOrdinalBottom(this.xScale));
      }

      return xaxis;
    },
    yAxis() {
      return axisLeft(this.yScale).ticks(5);
    },
  },
  watch: {
    filteredData() {
      this.data = this.group.all();

      if (this.selected.length && !this.dimension.currentFilter()) {
        this.selected = [];
        this.cat_cbs = [];
      }
    },
    cohort() {
      this.updateSelectionFromCohortQuery();
    },
    selected(new_sel) {
      var sel_h = {};
      new_sel.forEach(s => {
        sel_h[s] = true;
      });
      // update checkboxes to match
      var new_cat_cbs = [];
      this.data.forEach(d => {
        var sel = sel_h[d.key];
        if (sel) new_cat_cbs.push(d.key);
      });
      this.cat_cbs = new_cat_cbs;
    },
    // category checkboxes modified
    cat_cbs(new_cbs) {
      // selected bars
      var sel_b = {};
      this.selected.forEach(s => {
        sel_b[s] = true;
      });

      // selected checkboxes
      var sel_c = {};
      new_cbs.forEach(s => {
        sel_c[s] = true;
      });

      // compare checkbox state with current selection
      this.data.forEach(d => {
        var k = d.key;
        var bar_sel = sel_b[k];
        var cb_val = sel_c[k];

        if (cb_val && !bar_sel) {
          this.selectOrDeselectBar(k);
        } else if (!cb_val && bar_sel) {
          this.selectOrDeselectBar(k);
        }
      });
    },
    showFilterHelp(show) {
      this.showHelpChip = show;
    },
  },
  created() {
    const dimension = this.dimensions[this.dimensionName];
    this.dimension = dimension;
    this.group = dimension.group();
    this.data = this.group.all();

    var popCounts = {};
    this.unfilteredData.forEach(d => {
      var v = dimension.accessor(d);

      if (!(v in popCounts)) {
        popCounts[v] = 0;
      }
      popCounts[v] += 1;
    });
    var popData = [];
    for (var k in popCounts) {
      var c = popCounts[k];
      popData.push({ key: k, value: c });
    }
    this.populationData = popData;
    this.updateSelectionFromCohortQuery();
  },
  destroyed() {
    this.clearFilter({
      dimension: this.dimensionName,
    });
  },
  mounted() {
    this.container = this.$refs.container;
    this.resizeChart();
  },
  methods: {
    ...mapActions('cohortManager', {
      addFilter: actions.ADD_FILTER,
      clearFilter: actions.CLEAR_FILTER,
    }),
    getFill(key) {
      if (!this.selected.length || this.selected.includes(key)) {
        return colors['cohort'];
      }
      return colors['population'];
    },
    selectBar(key) {
      // already selected
      if (this.selected.includes(key)) {
        return;
      }
      this.selectOrDeselectBar(key);
    },
    deselectBar(key) {
      // already deselected
      if (!this.selected.includes(key)) {
        return;
      }
      this.selectOrDeselectBar(key);
    },
    selectOrDeselectBar(key) {
      if (this.selected.includes(key)) {
        this.selected = this.selected.filter(d => d !== key);
      } else {
        this.selected.push(key);
      }

      if (this.selected.length) {
        this.addFilter({
          dimension: this.dimensionName,
          filter: d => this.selected.includes(d),
          query: this.selected.map(k => ({
            value: k,
          })),
        });
      } else {
        this.clearFilter({
          dimension: this.dimensionName,
        });
      }
    },
    userClickedBar(key) {
      this.selectOrDeselectBar(key);
      this.$emit('userChangedVariable', this.dimensionName);
    },
    resizeChart() {
      this.height = 150;
      this.width = 350;
    },
    updateSelectionFromCohortQuery() {
      // If there is a cohort selected then apply the appropriate
      // queries to the chart
      if (this.hasUserSelectedCohort) {
        const queries = this.findCohortQuery(this.dimensionName);
        // we want to delay updating the chart a cycle until
        // the chart is actually mounted to the DOM
        this.$nextTick(() => {
          queries.forEach(queryForThisChart =>
            this.selectOrDeselectBar(queryForThisChart.value)
          );
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
div.v-input--checkbox {
  padding: 0px;
}
</style>
