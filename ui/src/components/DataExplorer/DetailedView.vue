<template>
  <div class="ma-0" min-height="400px" fill-height>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2">
              Detailed View<span v-if="detailedView" class="subtitle-1">
                - {{ detailedView.label }}</span
              >
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid fill-width class="pa-0 ma-0 pt-2 pl-2">
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
        <v-checkbox
          v-model="draw_raw"
          label="Show Raw Data"
          class="pl-3"
        ></v-checkbox>
        <v-checkbox
          v-model="draw_mean"
          label="Overlay Mean/SD"
          class="pl-3"
        ></v-checkbox>
        <v-checkbox
          v-model="show_population_counts"
          label="Show Study Population Counts"
          class="pl-3"
        ></v-checkbox>
        <v-checkbox
          v-model="show_first_last_visit"
          label="Show First/Last Visit"
          class="pl-3"
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
          >
            SELECT OUTCOME VARIABLE
          </div>

          <detailed-view-chart
            v-else
            :variable="detailedView"
            :dimension-name="detailedView.id"
            :line-style="line_style"
            :draw-mean="draw_mean"
            :draw-raw="draw_raw"
            :show-population-counts="show_population_counts"
            :show-first-last-visit="show_first_last_visit"
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
  data() {
    return {
      line_style: 'bezier',
      draw_mean: true,
      draw_raw: true,
      show_population_counts: false,
      show_first_last_visit: true,
      xaxis: 'visit_event',
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      detailedView: state.DETAILED_VIEW,
    }),
  },
  methods: {},
};
</script>

<style lang="scss" scoped></style>
