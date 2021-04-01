<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow pa-0 ma-0">
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              >ANALYTICS
              <v-divider vertical class="ml-4 mr-4"> </v-divider>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <div v-show="expanded">
      <v-container
        v-if="pvals_request_status == null || pvals_request_status == 'loading'"
        fluid
        fill-height
      >
        <v-row>
          <v-col cols="12">
            <v-subheader class="subheading primary--text text--lighten-4">
              <div v-if="pvals_request_status == null">
                Add variables and apply filters to them to view statistical test
                results for all outcome variables.
              </div>
              <div v-else-if="pvals_request_status == 'loading'">
                <v-subheader class="title primary--text text--lighten-4">
                  <loading-spinner />
                </v-subheader>
              </div>
            </v-subheader>
          </v-col>
        </v-row>
      </v-container>

      <v-container v-else fluid fill-height class="ma-0 pa-0">
        <v-row v-if="showHelpChip" class="ma-0 pa-0 mt-2 ml-2">
          <v-col cols="12" class="ma-0 pa-0">
            <v-chip
              v-if="showHelpChip"
              label
              close
              color="#4caf50"
              class="font-weight-bold white--text pa-3"
              @click:close="showHelpChip = false"
              >Review analytics for Selected Cohort vs. Remainder.</v-chip
            >
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="6" class="pb-0">
            <div class="ml-2">
              <v-toolbar-title
                class="primary--text subtitle-1 font-weight-bold mb-1"
                >Comparing</v-toolbar-title
              >

              <div class="ma-0 pa-0">
                <v-tooltip bottom color="primary">
                  <template v-slot:activator="{ on: tooltip }">
                    <span v-on="{ ...tooltip }">
                      <v-chip
                        label
                        color="primary"
                        class="white--text title mr-2 mb-2"
                        :style="'background: ' + colors['cohort']"
                        >{{ cohortSize }}</v-chip
                      >
                      <span class="black--text text-body-1"
                        >Selected Cohort</span
                      >
                    </span>
                  </template>
                  <span class="subtitle-1">
                    {{ cohortSize }} subject{{ cohortSize == 1 ? '' : 's' }} in
                    selected cohort
                  </span>
                </v-tooltip>
              </div>

              <div class="ma-0 pa-0">
                <v-tooltip bottom color="primary">
                  <template v-slot:activator="{ on: tooltip }">
                    <span v-on="{ ...tooltip }">
                      <v-chip
                        label
                        class="black--text title mr-2"
                        :style="'background: ' + colors['population']"
                        >{{ remainderSize }}</v-chip
                      >
                      <span class="black--text text-body-1">Remainder</span>
                    </span>
                  </template>
                  <span class="subtitle-1">
                    {{ remainderSize }} subject{{
                      remainderSize == 1 ? '' : 's'
                    }}
                    in remainder
                  </span>
                </v-tooltip>
              </div>
            </div>
          </v-col>

          <v-col cols="6" class="pb-0">
            <div v-if="collection.is_longitudinal" class="ml-2">
              <v-toolbar-title
                class="primary--text subtitle-1 font-weight-bold mb-1"
                >Outcome Measure</v-toolbar-title
              >
              <v-radio-group
                v-model="selectedComparisonMeasure"
                hide-details
                class="ma-0 pa-0"
              >
                <v-radio
                  v-for="m in ['Change', 'First Visit', 'Last Visit']"
                  :key="m"
                  :label="m"
                  :value="m"
                ></v-radio>
              </v-radio-group>
            </div>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" class="pt-0">
            <div align="center">
              <div class="pa-1 py-4">
                <v-chip
                  v-for="pv in pval_thresholds"
                  :color="getPvalColor(pv)"
                  :class="
                    (colorScheme == 'brewer5' && pv == '0.001'
                      ? 'white--text'
                      : '') + ' px-2 mx-1'
                  "
                  :style="
                    pval_threshold == pv
                      ? 'border: 2px solid rgb(236,118,188);'
                      : 'border: 2px solid black;'
                  "
                  @click="setPvalThreshold(pv)"
                >
                  p &lt; {{ pv }}</v-chip
                >
              </div>

              <v-data-table
                v-if="pvals_request_status == 'loaded'"
                :headers="headers"
                :items="pvals"
                dense
                hide-default-footer
                disable-pagination
                sort-by="pval"
              >
                <template v-slot:item="props">
                  <!--                  <tr :class="getVariableClass(props.item)"> -->
                  <tr>
                    <td class="text-subtitle-1 text-xs-left">
                      <v-tooltip top color="primary">
                        <template v-slot:activator="{ on: tooltip }">
                          <span v-on="{ ...tooltip }">
                            {{
                              useLongScaleNames
                                ? props.item.label
                                : props.item.abbreviation
                            }}
                          </span>
                        </template>
                        <span
                          v-html="
                            useLongScaleNames
                              ? props.item.description
                              : props.item.label
                          "
                        ></span>
                      </v-tooltip>
                    </td>
                    <td class="text-subtitle-1 text-xs-left">
                      <v-tooltip bottom color="primary">
                        <template v-slot:activator="{ on: tooltip }">
                          <div v-on="{ ...tooltip }">
                            {{ props.item.test_abbrev }}
                          </div>
                        </template>
                        <span v-html="props.item.test_name"></span>
                      </v-tooltip>
                    </td>
                    <td
                      v-if="props.item.error"
                      class="text-subtitle-1 text-xs-left error"
                      colspan="2"
                    >
                      {{ props.item.error }}
                    </td>
                    <td
                      v-if="!props.item.error"
                      class="text-subtitle-1 text-xs-right"
                    >
                      <v-tooltip
                        v-if="collection.is_longitudinal"
                        bottom
                        color="primary"
                      >
                        <template v-slot:activator="{ on: tooltip }">
                          <div v-on="{ ...tooltip }">
                            {{ props.item.effect_size | formatEffectSize }}
                          </div>
                        </template>
                        <span>{{ props.item.effect_size_descr }}</span>
                      </v-tooltip>

                      <v-tooltip v-else bottom color="primary">
                        <template v-slot:activator="{ on: tooltip }">
                          <div v-on="{ ...tooltip }">
                            {{ props.item.chi2 | formatChiSquared }}
                          </div>
                        </template>
                        <span>Chi-squared statistic</span>
                      </v-tooltip>
                    </td>
                    <td
                      v-if="!props.item.error"
                      class="text-subtitle-1 text-xs-right"
                      :style="{
                        backgroundColor: pval_table_cell_color(props.item.pval),
                        color: pval_table_text_color(props.item.pval),
                      }"
                    >
                      {{ props.item.pval | formatPValue }}
                    </td>
                  </tr>
                </template>
              </v-data-table>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import { format } from 'd3-format';
import { colors } from '@/utils/colors';

export default {
  filters: {
    formatPValue(pvalue) {
      if (pvalue == null) {
        return '-';
      }
      if (pvalue < 0.001) {
        return '< 0.001';
      } else {
        return format('.4f')(pvalue);
      }
    },
    formatEffectSize(size) {
      return size == null ? '-' : format('.2f')(size);
    },
    formatChiSquared(cs) {
      return cs == null ? '-' : format('.2f')(cs);
    },
  },
  props: {
    colorScheme: {
      type: String,
      required: false,
      default: 'val100',
    },
    showReviewHelp: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      highlight_by_pval: false,
      pval_thresholds: [1, 0.1, 0.05, 0.01, 0.001],
      pvt: 'None',
      expanded: true,
      selectedComparisonMeasure: 'Last Visit',
      colors: colors,
      showHelpChip: false,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      pvals: state.PVALS,
      pvals_request_status: state.PVALS_REQUEST_STATUS,
      pval_threshold: state.PVAL_THRESHOLD,
      collection: state.COLLECTION,
      comparisonMeasure: state.COMPARISON_MEASURE,
      useLongScaleNames: state.USE_LONG_SCALE_NAMES,
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
    }),
    headers() {
      var headers = [
        {
          text: 'Variable',
          align: 'left',
          sortable: true,
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Test',
          align: 'left',
          sortable: true,
          value: 'test_name',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: this.collection.is_longitudinal ? 'Effect Size' : 'Chi2',
          align: 'left',
          sortable: true,
          value: 'effect_size',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'p-Value',
          align: 'left',
          sortable: true,
          value: 'pval',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ];
      return headers;
    },
    cohortSize() {
      return this.filteredData.length;
    },
    remainderSize() {
      return this.unfilteredData.length - this.filteredData.length;
    },
  },
  watch: {
    pvt(newPvt) {
      this.setPvalThreshold(newPvt);
    },
    selectedComparisonMeasure(measure) {
      this.setComparisonMeasure(measure);
    },
    showReviewHelp(show) {
      this.showHelpChip = show;
    },
  },
  created() {
    this.pvt = this.pval_threshold;
    this.selectedComparisonMeasure = this.comparisonMeasure;
  },
  methods: {
    ...mapActions('cohortManager', {
      setPvalThreshold: actions.SET_PVAL_THRESHOLD,
      setComparisonMeasure: actions.SET_COMPARISON_MEASURE,
    }),
    updatePval(newPval) {
      this.setPvalThreshold(newPval);
    },
    getVariableClass(v) {
      if (v.pval != null && v.pval < this.pval_threshold && !v.error) {
        return 'highlight-var-row';
      }
      return '';
    },
    getPvalColor(pv) {
      var c = colors['pvals'][pv.toString() + '-' + this.colorScheme];
      if (c) {
        return c['color'];
      } else {
        return 'white';
      }
    },
    expandClicked() {
      this.expanded = !this.expanded;
    },
    pval_table_cell_aux(pval, which) {
      let ccl = this.colors['pvals']['1' + '-' + this.colorScheme][which];
      if (pval < 0.001) {
        ccl = this.colors['pvals']['0.001' + '-' + this.colorScheme][which];
      } else if (pval < 0.01) {
        ccl = this.colors['pvals']['0.01' + '-' + this.colorScheme][which];
      } else if (pval < 0.05) {
        ccl = this.colors['pvals']['0.05' + '-' + this.colorScheme][which];
      } else if (pval < 0.1) {
        ccl = this.colors['pvals']['0.1' + '-' + this.colorScheme][which];
      }
      return ccl;
    },
    pval_table_cell_class(pval) {
      return this.pval_table_cell_aux(pval, 'class');
    },
    pval_table_cell_color(pval) {
      return this.pval_table_cell_aux(pval, 'color');
    },
    pval_table_text_color(pval) {
      if (this.colorScheme == 'brewer5') {
        if (pval < 0.001) {
          return 'white';
        }
      }
      return 'black';
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

/* Transition effect for changing routes */
.fade-enter-active,
.fade-leave-active {
  transition-duration: 0.3s;
  transition-property: opacity;
  transition-timing-function: ease;
}
.fade-enter,
.fade-leave-active {
  opacity: 0;
}
</style>
