<template>
  <div>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              ><v-icon x-large class="pr-2" color="primary">analytics</v-icon>
              {{ title }}

              <v-divider vertical class="ml-4 mr-4"> </v-divider>

              <v-tooltip bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <v-chip
                      label
                      color="primary"
                      class="white--text title mr-2"
                      >{{ analysis.cohorts.length }}</v-chip
                    >
                    <span class="black--text text-body-1"
                      >Cohort{{ analysis.cohorts.length == 1 ? '' : 's' }}</span
                    >
                  </span>
                </template>
                <span class="subtitle-1">
                  {{ analysis.cohorts.map(c => c.label).join(', ') }}
                </span>
              </v-tooltip>

              <v-divider vertical class="ml-4 mr-4"> </v-divider>

              <v-tooltip bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <v-chip
                      label
                      color="primary"
                      class="white--text title mr-2"
                      >{{ analysis.outcomeVariables.length }}</v-chip
                    >
                    <span class="black--text text-body-1"
                      >Scale{{
                        analysis.outcomeVariables.length == 1 ? '' : 's'
                      }}</span
                    >
                  </span>
                </template>
                <span class="subtitle-1">
                  {{
                    analysis.outcomeVariables
                      .map(ov => ov.abbreviation)
                      .join(', ')
                  }}
                </span>
              </v-tooltip>

              <v-divider vertical class="ml-4 mr-4"> </v-divider>

              <v-tooltip bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <span class="black--text text-body-1">Comparing: </span>
                    <v-chip
                      label
                      color="primary"
                      class="white--text title mr-2"
                      >{{ analysis.input.comparisonFieldDescr }}</v-chip
                    >
                  </span>
                </template>
                <span class="subtitle-1">
                  Comparing {{ analysis.input.comparisonFieldLongDescr }}
                </span>
              </v-tooltip>

              <v-divider vertical class="ml-4 mr-4"> </v-divider>

              <v-tooltip bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <span class="black--text text-body-1">Status: </span>
                    <v-chip
                      label
                      :color="statusColor[analysis.status]"
                      class="white--text title mr-2"
                      >{{ analysis.status }}</v-chip
                    >
                  </span>
                </template>
                <span v-if="analysis.status == 'Failed'" class="subtitle-1">
                  {{ analysis.error }}
                </span>
                <span v-else class="subtitle-1">
                  {{ analysis.status }} at
                  {{ analysis.statusTime | formatDate }}
                </span>
              </v-tooltip>

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
            <splitpanes
              ref="splitter"
              class="default-theme"
              @resize="splitPaneResized"
            >
              <pane size="45" min-size="15" max-size="60" class="pb-1">
                <v-sheet color="white" height="100%" class="rounded-lg shadow">
                  <v-tabs v-model="leftTab" light>
                    <v-tab key="cohorts">Input Cohorts</v-tab>
                    <v-tab key="analytics">Analytics/Scales</v-tab>
                    <v-tab key="statistics">Cohort Statistics</v-tab>
                  </v-tabs>

                  <v-tabs-items v-model="leftTab" class="pt-3">
                    <v-tab-item key="cohorts">
                      <cohort-table
                        :cohorts="analysis.cohorts"
                        :select-cohorts="visibleCohorts"
                        :outcome-var="detailedView"
                        :show-title-bar="false"
                        :expanded="expandAnalytics"
                        report-max-overlap
                        show-select
                        show-colors
                        @selectedCohorts="updateVisibleCohorts"
                      />
                    </v-tab-item>

                    <v-tab-item key="analytics">
                      <analytics-panel
                        :selected-variable="detailedView"
                        :anova-pvals="analysis.pvals"
                        :anova-pvals-input="analysis.input"
                        :outcome-variables="analysis.outcomeVariables"
                        :show-category-icons="true"
                        :show-title-bar="false"
                        autoselect-first-variable
                        :expanded="expandAnalytics"
                        color-scheme="brewer5"
                        @variableSelected="variableSelected"
                        @expandClicked="analyticsExpandClicked"
                      />
                    </v-tab-item>

                    <v-tab-item key="statistics">
                      <summary-stats
                        :predictor-variables="analysis.predictorVariables"
                        :outcome-variables="analysis.outcomeVariables"
                        :cohorts="analysis.cohorts"
                        :show-category-icons="true"
                        :show-title-bar="false"
                        :comparison-field="analysis.input.comparisonField"
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
                        ref="boxplots"
                        :cohorts="visibleCohorts"
                        :show-title-bar="false"
                        :outcome-var="detailedView"
                        :max-cohorts="analysis.cohorts.length"
                        :row-height="70"
                        :row-pad="12"
                        :bar-pad="5"
                      />
                      <stacked-bars
                        v-else
                        ref="stackedbars"
                        :cohorts="visibleCohorts"
                        :show-title-bar="false"
                        :outcome-var="detailedView"
                        :max-cohorts="analysis.cohorts.length"
                        :row-height="70"
                        :row-pad="12"
                        :bar-pad="5"
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
import SummaryStats from '@/components/AnalysisSummary/SummaryStats.vue';
import DetailedView from '@/components/DataExplorer/DetailedView.vue';
import BoxPlots from '@/components/AnalysisSummary/BoxPlots.vue';
import StackedBars from '@/components/AnalysisSummary/StackedBars.vue';
import { colors } from '@/utils/colors';

export default {
  components: {
    AnalyticsPanel,
    BoxPlots,
    CohortTable,
    SummaryStats,
    DetailedView,
    StackedBars,
    Splitpanes,
    Pane,
  },
  filters: {
    formatDate(ts) {
      // note that toISOString is going to give us UTC
      return new Date(ts);
    },
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
      status: 'Submitted',
      error: null,
      statusTime: null,
      statusColor: {
        Submitted: 'primary',
        Running: 'secondary',
        Completed: 'success',
        Failed: 'error',
      },
    };
  },
  watch: {
    analysis(a) {
      if (a != null) {
        this.visibleCohorts = this.analysis.cohorts;
      }
    },
    rightTab(rt) {
      // workaround for resize problem #596
      if (rt == 0) {
        const dv = this.$refs.dview;
        setTimeout(async function() {
          if (dv) dv.onResize();
        }, 500);
      } else if (rt == 1) {
        const bp = this.$refs.boxplots;
        const sb = this.$refs.stackedbars;
        setTimeout(async function() {
          if (bp) bp.onResize();
          if (sb) sb.onResize();
        }, 500);
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
      // keep visibleCohorts sorted in the same order as cohorts
      var vcids = {};
      vc.forEach(c => {
        vcids[c.id] = true;
      });
      this.visibleCohorts = this.analysis.cohorts.filter(c => vcids[c.id]);
    },
    deleteAnalysis() {
      this.$emit('deleteAnalysis');
    },
    getComparisonFieldDescription(cfield) {
      const descrs = {
        change: 'Change from first visit - last visit',
        firstVisit: 'First visit',
        lastVisit: 'Last visit',
      };
      return descrs[cfield];
    },
    splitPaneResized(evt) {
      var psize = evt[0].size;
      this.expandAnalytics = psize > 30;

      if (this.rightTab == 0) {
        this.$refs.dview.onResize();
      } else if (this.rightTab == 1) {
        if (
          this.detailedView &&
          this.detailedView.data_category == 'Continuous'
        ) {
          this.$nextTick(() => this.$refs.boxplots.onResize());
        } else {
          this.$nextTick(() => this.$refs.stackedbars.onResize());
        }
      }
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
