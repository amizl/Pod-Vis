<template>
  <div class="ma-0" min-height="400px" fill-height>
    <v-container
      v-if="showTitleBar"
      v-resize="onResize"
      fluid
      fill-width
      class="ma-0 pa-0"
    >
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2">
              Detailed View
            </v-card-title>

            <v-card-title class="primary--text pa-0 pl-3">
              <v-tooltip v-if="detailedView" bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <img
                    :src="'/images/' + detailedView.category + '-icon-128.png'"
                    :title="detailedView.category"
                    style="height:1.75em"
                    class="ma-1"
                    v-on="{ ...tooltip }"
                  />
                </template>
                <span>{{ detailedView.category }}</span>
              </v-tooltip>
              <span v-if="detailedView" class="subtitle-1">
                {{ detailedView.abbreviation }}
              </span>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-container v-else fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card-title class="primary--text pa-0 pt-3 pl-2">
            <v-tooltip v-if="detailedView" bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <img
                  :src="'/images/' + detailedView.category + '-icon-128.png'"
                  :title="detailedView.category"
                  style="height:1.75em"
                  class="ma-1"
                  v-on="{ ...tooltip }"
                />
              </template>
              <span>{{ detailedView.category }}</span>
            </v-tooltip>

            <v-tooltip v-if="detailedView" top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span v-on="{ ...tooltip }">
                  {{ detailedView.abbreviation }}
                </span>
              </template>
              <span v-html="detailedView.label"></span>
            </v-tooltip>
          </v-card-title>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid fill-width class="pa-0 ma-0 pl-2">
      <v-row class="pl-2" align="center">
        <!--
        <span class="subheading primary--text mt-3 mr-2">Style:</span>
        <v-btn-toggle v-model="line_style">
         <v-btn text color="primary" class="white--text mr-2 py-1" value="bezier">BEZIER</v-btn>
         <v-btn text color="#3FB551" class="white--text mr-2 py-1" value="line">LINE</v-btn>
        </v-btn-toggle>
	-->
        <!--
        <span class="pl-2">X-Axis:</span>
        <v-btn-toggle v-model="xaxis" class="pl-2" mandatory>
          <v-btn text color="primary" class="white--text" value="visits"
            >VISITS</v-btn
          >
          <v-btn text color="primary" class="white--text" value="days"
            >DAYS</v-btn
          >
        </v-btn-toggle>
-->
        <span class="pl-2">Show:</span>
        <v-checkbox
          v-if="!isDetailedViewCategorical"
          v-model="draw_raw"
          label="Raw Data"
          class="pl-3"
          :disabled="isDetailedViewCategorical"
        ></v-checkbox>
        <v-checkbox
          v-if="!isDetailedViewCategorical"
          v-model="draw_mean"
          label="Mean/SD"
          class="pl-3"
          :disabled="isDetailedViewCategorical"
        ></v-checkbox>
        <v-checkbox
          v-if="!isDetailedViewCategorical"
          v-model="show_population_counts"
          label="Population Counts"
          class="pl-3"
          :disabled="isDetailedViewCategorical"
        ></v-checkbox>
        <v-checkbox
          v-model="show_first_last_visit"
          label="First/Last Visit"
          class="pl-3"
        ></v-checkbox>
        <v-checkbox
          v-model="show_all_timepoints"
          label="All Timepoints"
          class="pl-3"
        ></v-checkbox>
        <v-checkbox
          v-if="isDetailedViewCategorical"
          v-model="show_percentages"
          label="Percentages"
          class="pl-3"
          :disabled="!isDetailedViewCategorical"
        ></v-checkbox>
      </v-row>
    </v-container>

    <v-divider></v-divider>

    <v-container fluid fill-height min-height="400px">
      <v-row class="pa-0 ma-0">
        <v-col cols="12" class="pa-0 ma-0">
          <div
            v-if="!detailedView"
            class="display-1 primary--text text--lighten-5 pt-5 mt-5"
            align="center"
          >
            NO VARIABLE SELECTED
          </div>

          <div
            v-else-if="!visibleCohorts || visibleCohorts.length == 0"
            class="display-1 primary--text text--lighten-5 pt-5 mt-5"
            align="center"
          >
            NO COHORTS SELECTED
          </div>

          <detailed-view-chart
            v-else
            ref="dview_chart"
            :variable="detailedView"
            :dimension-name="detailedView.id"
            :visible-cohorts="visibleCohorts"
            :line-style="line_style"
            :draw-mean="draw_mean"
            :draw-raw="draw_raw"
            :show-population-counts="show_population_counts"
            :show-first-last-visit="show_first_last_visit"
            :show-all-timepoints="show_all_timepoints"
            :show-percentages="show_percentages"
            :xaxis="xaxis"
            class="pa-0 ma-0"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';
import DetailedViewChart from '@/components/DataExplorer/DetailedViewChart.vue';

export default {
  components: {
    DetailedViewChart,
  },
  props: {
    detailedView: {
      type: Object,
      required: false,
      default: null,
    },
    showTitleBar: {
      type: Boolean,
      required: false,
      default: true,
    },
    visibleCohorts: {
      type: Array,
      required: true,
      default: () => [],
    },
  },
  data() {
    return {
      line_style: 'bezier',
      draw_mean: true,
      draw_raw: false,
      show_population_counts: false,
      show_first_last_visit: true,
      show_all_timepoints: true,
      show_percentages: false,
      xaxis: 'visit_event',
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      collection: state.COLLECTION,
    }),
    isDetailedViewCategorical() {
      return (
        this.detailedView && this.detailedView.data_category == 'Categorical'
      );
    },
  },
  watch: {
    detailedView(ndv) {
      // find corresponding observation variable in collection
      // and determine if first/last visit are by event or number
      var obs_v = null;
      this.collection.observation_variables_list.forEach(v => {
        if (v.ontology.id == ndv.id) obs_v = v;
      });
      if (obs_v != null && obs_v.first_visit_event != null) {
        this.xaxis = 'visit_event';
      } else {
        this.xaxis = 'visit_num';
      }
    },
  },
  methods: {
    // workaround to force DetailedViewChart resize when expandAnalytics toggled
    onResize() {
      if (this.$refs.dview_chart) {
        this.$refs.dview_chart.onResize();
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
