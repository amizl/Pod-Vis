<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-card-title class="title primary--text">Detailed View<span v-if="detailedView">&nbsp;-&nbsp;{{ detailedView.label }}</span></v-card-title>

    <v-toolbar card dense flat color="white rounded-lg">
      <v-toolbar-items>
        <span class="subheading primary--text mt-3 mr-3">Draw:</span>
        <v-btn-toggle v-model="style"  @change="doStyleChange()">
         <v-btn text color="primary" class="white--text mr-2 py-1" value="bezier">BEZIER</v-btn>
         <v-btn text color="#3FB551" class="white--text mr-2 py-1" value="line">LINE</v-btn>
        </v-btn-toggle>
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
      style: 'bezier',
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      detailedView: state.DETAILED_VIEW,
      lineStyle: state.LINE_STYLE,
    }),
  },
  methods: {
    ...mapActions('dataExplorer', {
      setLineStyle: actions.SET_LINE_STYLE,
    }),
    doStyleChange() {
      if (typeof this.style !== 'undefined') {
        this.setLineStyle(this.style);
      }
    }
  }
};
</script>

<style lang="scss" scoped></style>
