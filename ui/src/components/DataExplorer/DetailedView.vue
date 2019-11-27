<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-card-title class="title primary--text">Detailed View<span v-if="detailedView">&nbsp;-&nbsp;{{ detailedView.label }}</span></v-card-title>

    <v-toolbar card dense flat color="white rounded-lg">
      <v-toolbar-items>
<!--
        <span class="subheading primary--text mt-3 mr-2">Style:</span>
        <v-btn-toggle v-model="line_style">
         <v-btn text color="primary" class="white--text mr-2 py-1" value="bezier">BEZIER</v-btn>
         <v-btn text color="#3FB551" class="white--text mr-2 py-1" value="line">LINE</v-btn>
        </v-btn-toggle>
-->
        <span class="subheading primary--text mt-3 mr-2 ml-3">X-Axis:</span>
        <v-btn-toggle v-model="xaxis">
         <v-btn text color="primary" class="white--text mr-2 py-1" value="visits">VISITS</v-btn>
         <v-btn text color="#3FB551" class="white--text mr-2 py-1" value="days">DAYS</v-btn>
        </v-btn-toggle>

       <span class="subheading primary--text mt-3 mr-2 ml-3">Show Raw Data:</span>
       <v-checkbox class="mt-2" v-model="draw_raw">
       </v-checkbox>

       <span class="subheading primary--text mt-3 mr-2 ml-3">Overlay Mean/SD:</span>
       <v-checkbox class="mt-2" v-model="draw_mean">
       </v-checkbox>

      </v-toolbar-items>
      </v-toolbar>

      <v-divider></v-divider>
      <v-container fluid fill-height>
        <v-layout column align-center justify-center fill-height>
          <v-subheader
            v-if="!detailedView"
            class="display-1 primary--text text--lighten-5"
          >
            SELECT OUTCOME VARIABLE
          </v-subheader>

    <!-- work in progress -->
     <detailed-view-chart v-else
        :variable="detailedView"
        :dimension-name="detailedView.id"
  	:line-style="line_style"
        :draw-mean="draw_mean"
        :draw-raw="draw_raw"
  	:xaxis="xaxis"
      />

       </v-layout>
      </v-container>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/dataExplorer/types';
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
  methods: {
  }
};
</script>

<style lang="scss" scoped></style>
