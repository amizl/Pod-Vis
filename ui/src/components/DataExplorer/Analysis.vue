<template>
  <div>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              ><v-icon large class="pr-2" color="primary">analytics</v-icon>
              {{ title }}
              <v-spacer />
              <v-toolbar-items>
                <v-icon color="primary" class="mx-4" @click="deleteAnalysis"
                  >delete</v-icon
                >

                <v-icon v-if="expanded" @click="expanded = false"
                  >expand_less</v-icon
                >
                <v-icon v-else @click="expanded = true">expand_more</v-icon>
              </v-toolbar-items>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-sheet v-show="expanded" color="white" class="rounded-lg shadow pt-2">
      <v-container fluid fill-width class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <splitpanes class="default-theme">
              <pane size="45" min-size="30" max-size="60" class="pb-1">
                <v-sheet color="white" height="100%" class="rounded-lg shadow">
                  <v-tabs v-model="leftTab" light>
                    <v-tab key="analytics">Analytics/Scales</v-tab>
                    <v-tab key="cohorts">Input Cohorts</v-tab>
                  </v-tabs>

                  <v-tabs-items v-model="leftTab" class="pt-3">
                    <v-tab-item key="analytics">
                      <analytics-panel
                        :selected-variable="detailedView"
                        :show-category-icons="true"
                        :show-title-bar="false"
                        autoselect-first-variable
                        :expanded="expandAnalytics"
                        color-scheme="brewer5"
                        @variableSelected="variableSelected"
                        @expandClicked="analyticsExpandClicked"
                      />
                    </v-tab-item>

                    <v-tab-item key="cohorts">
                      <cohort-table
                        :cohorts="analysis.cohorts"
                        :select-cohorts="visibleCohorts"
                        :outcome-var="detailedView"
                        :show-title-bar="false"
                        report-max-selected-overlap
                        show-select
                        show-colors
                        @selectedCohorts="updateVisibleCohorts"
                      />
                    </v-tab-item>
                  </v-tabs-items>
                </v-sheet>
              </pane>

              <pane size="65" class="pb-1">
                <v-sheet
                  color="white"
                  height="100%"
                  min-height="400px"
                  class="rounded-lg shadow"
                >
                  <v-tabs v-model="rightTab" light>
                    <v-tab key="lview">Detailed View</v-tab>
                    <v-tab key="boxplots">Boxplots/Bar graphs</v-tab>
                  </v-tabs>

                  <v-tabs-items v-model="rightTab">
                    <v-tab-item key="lview">
                      <detailed-view
                        ref="dview"
                        :detailed-view="detailedView"
                        :visible-cohorts="visibleCohorts"
                        :show-title-bar="false"
                        min-height="400px"
                      />
                    </v-tab-item>

                    <v-tab-item key="boxplots">
                      <box-plots
                        v-if="
                          detailedView &&
                            detailedView.data_category == 'Continuous'
                        "
                        :cohorts="visibleCohorts"
                        :show-title-bar="false"
                        :outcome-var="detailedView"
                      />
                      <stacked-bars
                        v-else
                        :cohorts="visibleCohorts"
                        :show-title-bar="false"
                        :outcome-var="detailedView"
                      />
                    </v-tab-item>
                  </v-tabs-items>
                </v-sheet>
              </pane>
            </splitpanes>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>
  </div>
</template>

<script>
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

import CohortTable from '@/components/common/CohortTable.vue';
import AnalyticsPanel from '@/components/DataExplorer/AnalyticsPanel.vue';
import DetailedView from '@/components/DataExplorer/DetailedView.vue';
import BoxPlots from '@/components/AnalysisSummary/BoxPlots.vue';
import StackedBars from '@/components/AnalysisSummary/StackedBars.vue';
import { colors } from '@/utils/colors';

export default {
  components: {
    AnalyticsPanel,
    BoxPlots,
    CohortTable,
    DetailedView,
    StackedBars,
    Splitpanes,
    Pane,
  },
  props: {
    title: {
      type: String,
      required: false,
      default: 'Cohorts',
    },
    analysis: {
      type: Object,
      required: true,
      default: {},
    },
  },
  data() {
    return {
      expanded: true,
      expandAnalytics: true,
      detailedView: null,
      leftTab: null,
      rightTab: null,
      visibleCohorts: [],
    };
  },
  watch: {
    analysis(a) {
      if (a != null) {
        this.visibleCohorts = analysis.cohorts;
      }
    },
  },
  created() {
    if (this.analysis != null) {
      this.visibleCohorts = this.analysis.cohorts;
    }
  },
  methods: {
    variableSelected(nv) {
      this.detailedView = nv;
    },
    analyticsExpandClicked(nv) {
      this.expandAnalytics = nv;
    },
    updateVisibleCohorts(vc) {
      this.visibleCohorts = vc;
    },
    deleteAnalysis() {
      this.$emit('deleteAnalysis');
    },
  },
};
</script>
<style>
table.v-data-table thead tr th {
  font-size: 24px;
}
table.v-data-table tbody tr td {
  font-size: 24px;
}
</style>
