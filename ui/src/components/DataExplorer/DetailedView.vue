<template>
<div class="ma-1" min-height="400px" fill-height>
  <v-app-bar text dense class="rounded-lg">
    <v-toolbar-title class="title primary--text">
     Detailed View<span v-if="detailedView" class="subtitle-1">- {{ detailedView.label }}</span>
    </v-toolbar-title>
    <v-spacer />
   </v-app-bar>

    <v-container fluid fill-width class="pa-0 ma-0 pt-2 pl-2">
      <v-row class="pl-2" align="center">
 <!--
        <span class="subheading primary--text mt-3 mr-2">Style:</span>
        <v-btn-toggle v-model="line_style">
         <v-btn text color="primary" class="white--text mr-2 py-1" value="bezier">BEZIER</v-btn>
         <v-btn text color="#3FB551" class="white--text mr-2 py-1" value="line">LINE</v-btn>
        </v-btn-toggle>
	-->
        <span class="pl-2">X-Axis:</span> <v-btn-toggle v-model="xaxis" class="pl-2" mandatory>
            <v-btn
              text
              color="primary"
              class="white--text"
              value="visits"
              >VISITS</v-btn
            >
            <v-btn
              text
              color="primary"
              class="white--text"
              value="days"
              >DAYS</v-btn
            >
          </v-btn-toggle>
          <v-checkbox v-model="draw_raw" label="Show Raw Data" class="pl-3"></v-checkbox>
          <v-checkbox v-model="draw_mean" label="Overlay Mean/SD" class="pl-3"></v-checkbox>
       </v-row>
      </v-container>

      <v-divider></v-divider>
      
      <v-container fluid fill-height min-height="400px">
        <v-layout column align-center justify-center fill-height>
          <v-subheader
            v-if="!detailedView"
            class="display-1 primary--text text--lighten-5 pt-5 mt-5"
          >
            SELECT OUTCOME VARIABLE
          </v-subheader>

          <!-- work in progress -->
          <detailed-view-chart
            v-else
            :variable="detailedView"
            :dimension-name="detailedView.id"
            :line-style="line_style"
            :draw-mean="draw_mean"
            :draw-raw="draw_raw"
            :xaxis="xaxis"
	    class="pa-0 ma-0"
          />
        </v-layout>
      </v-container>
</v-layout>
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
      xaxis: 'visits',
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
