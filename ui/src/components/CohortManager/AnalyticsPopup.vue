<template>
  </v-sheet>
    <v-dialog v-model="dialog" scrollable max-width="50%">
      <v-card class="rounded-lg" style="border: 3px solid #3f51b5;">
        <v-card-title color="white" class="ma-0 pa-2" primary-title>
          <span class="primary--text text--darken-3 title"
            >Comparing: <span class="black--text">{{name}}</span></span>
	  <v-spacer></v-spacer>

              <v-tooltip bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <v-chip
                      label
                      class="black--text title mr-2"
                      :style="'background: ' + colors['population']"
                      >{{ unfilteredData.length }}</v-chip
                    >
                    <span class="black--text text-body-1">Study Population</span>
                  </span>
                </template>
                <span class="subtitle-1">
                  {{ unfilteredData.length }} subject{{
                    unfilteredData.length == 1 ? '' : 's'
                  }}
                  in study population
                </span>
              </v-tooltip>
	  
        </v-card-title>

	<v-divider></v-divider>
	
	<v-card-text>
      <v-container fluid fill-width class="ma-2 pa-0 mx-2">

	<!-- list of cohorts -->
	<v-row v-for="c in cohorts" :key="c.id" class="ma-0 pa-0" align="center">
	  <v-col cols="4" class="ma-0 pa-0">
	      <v-chip label :color="c.color" class="ma-1"><span class="white--text font-weight-bold">{{ c.subject_ids ? c.subject_ids.length : '?' }}</span></v-chip>
	      {{c.label}}
	  </v-col>
	  <v-col cols="8" class="ma-0 pa-0">
	    <v-icon>filter_alt</v-icon> {{c.query_string}}
	  </v-col>
	</v-row>

	<v-divider class="mx-3 my-2"></v-divider>
	
	<v-row class="ma-0 pa-0">
	  <v-col cols="12" class="ma-0 pa-0">
	    <span class="primary--text title">Outcome Measure: <span class="black--text">{{ comparisonMeasure }}</span></span>
	  </v-col>
	</v-row>

	<v-row class="ma-0 py-2">
	  <v-col cols="12" class="ma-0 pa-0">

	    <!-- p-values -->

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
	      p &lt; {{ pv }}</v-chip>
	  </v-col>
	</v-row>
	
	<!-- list of variables -->
	<v-row class="ma-0 pa-0 mb-3">
          <v-col cols="12" class="ma-0 pa-0" align="left">

            <div v-if="pvals_request_status == null || pvals_request_status == 'loading'">
                <v-subheader class="title primary--text text--lighten-4">
                  <loading-spinner />
                </v-subheader>
	    </div>
	    
	    <v-data-table
              v-if="pvals_request_status == 'loaded'"
              :headers="headers"
              :items="pvals"
              dense
              hide-default-footer
              disable-pagination
              sort-by="pval"
	      class="pa-0 ma-0 mr-3 pt-2"
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
<!--
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
-->
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
                            {{ props.item.fval | formatFValue }}
                          </div>
                        </template>
                        <span>1-way ANOVA F-Statistic</span>
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
                      <v-tooltip
                        bottom
                        color="primary"
                      >
                        <template v-slot:activator="{ on: tooltip }">
                          <div v-on="{ ...tooltip }">
			    {{ props.item.pval | formatPValue }}
                          </div>
                        </template>
                        <span>1-way ANOVA P-Value</span>
                      </v-tooltip>
                    </td>
                    <td
                      v-if="!props.item.error"
                      class="text-subtitle-1 text-xs-right"
                    >
		      <mini-boxplot
			:width="150"
			:height="14 * cohorts.length"
			:cohorts="cohorts"
			:output-var="abbrev_to_var[props.item.abbreviation]"
			:compare-by="comparisonMeasure"
			class="ma-0 pa-0">
		      </mini-boxplot>
                    </td>
                  </tr>
                </template>

	    </v-data-table>

	    <!--	    <div v-for="ov in outputVariables" :key="ov.id">
	      {{ ov.label }}
	    </div> -->
	  </v-col>
	</v-row>
      </v-container>
      </v-card-text>

      <v-divider></v-divider>
	
      <!-- save & close buttons -->
      <v-card-actions>

	<v-spacer></v-spacer>
	
	    <v-tooltip bottom color="primary">
	      <template v-slot:activator="{ on: tooltip }">
		<v-btn
		  class="primary white--text ma-0 px-2 mx-2"
		  @click="saveCohorts(cohorts, cohortPrefix)"
		  v-on="{ ...tooltip }"
		  >
		  Save {{name}} as {{cohorts.length}} cohorts
		</v-btn>
	      </template>
	      <span>Save cohorts</span>
	    </v-tooltip>

	    <v-tooltip bottom color="primary">
	      <template v-slot:activator="{ on: tooltip }">
		
		<v-btn
		  class="primary text--white ma-0 px-2 mx-2"
		  @click="dialog = false"
		  v-on="{ ...tooltip }"
		  >
		  <v-icon class="px-2">close</v-icon>
		  Close
		</v-btn>
	      </template>
	      <span>Close without saving new cohorts</span>
	    </v-tooltip>
	    
      </v-card-actions>
      
      </v-card>
    </v-dialog>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import { format } from 'd3-format';
import { colors } from '@/utils/colors';
import MiniBoxplot from '@/components/CohortManager/MiniBoxplot.vue';

export default {
  components: {
    MiniBoxplot,
  },
  filters: {
    formatFValue(fv) {
      if (fv == null) {
        return '-';
      }
      return `${format('.2f')(fv)}`;
    },
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
    name: {
      type: String,
      required: false,
      default: 'Cohorts',
    },
    colorScheme: {
      type: String,
      required: false,
      default: 'val100',
    },
    cohorts: {
      type: Array,
      required: true,
    },
    selectRangeFn: {
      type: Function,
      required: true,
    },
    cohortPrefix: {
      type: String,
      required: true,
    },
   },
  data() {
    return {
      highlight_by_pval: false,
      pval_thresholds: [1, 0.1, 0.05, 0.01, 0.001],
      pvt: 'None',
      expanded: true,
      colors: colors,
      dialog: false,
      abbrev_to_var: {},
     };
   },
   computed: {
    ...mapState('cohortManager', {
      pvals: state.ANOVA_PVALS,
      pvals_request_status: state.ANOVA_PVALS_REQUEST_STATUS,
      pval_threshold: state.PVAL_THRESHOLD,
      collection: state.COLLECTION,
      comparisonMeasure: state.COMPARISON_MEASURE,
      useLongScaleNames: state.USE_LONG_SCALE_NAMES,
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      inputVariables: state.INPUT_VARIABLES,
      outputVariables: state.OUTPUT_VARIABLES,
    }),
    headers() {
      var headers = [
        {
          text: 'Scale',
          align: 'left',
          sortable: true,
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
//        {
//          text: 'Test',
//          align: 'left',
//          sortable: true,
//          value: 'test_name',
//          class: 'text-subtitle-1 font-weight-bold',
//        },
        {
          text: 'F-Statistic',
          align: 'left',
          sortable: true,
          value: 'fval',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'p-Value',
          align: 'left',
          sortable: true,
          value: 'pval',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: '',
          align: 'left',
          sortable: false,
          value: 'boxplot',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ];
      return headers;
    },

   },
   watch: {
     cohorts() {
      // assign colors to cohorts
      let ind = 0;
      let n_colors = this.colors['cohorts'].length;
      this.cohorts.forEach(c => {
        if (!c.color) {
          c.color = this.colors['cohorts'][ind % n_colors];
          ind += 1;
        }
      });
     this.analyzeCohorts(this.cohorts);
    },
   },
   methods: {
    ...mapActions('cohortManager', {
      analyzeCohorts: actions.ANALYZE_COHORTS,
      setPvalThreshold: actions.SET_PVAL_THRESHOLD,
      setComparisonMeasure: actions.SET_COMPARISON_MEASURE,
      saveCohort: actions.SAVE_COHORT,
    }),
    updatePval(newPval) {
      this.setPvalThreshold(newPval);
    },
    show(ns) {
      this.pvt = this.pval_threshold;

      const outputVars = [];
      this.collection.observation_variables.forEach(v => {
        v.children.forEach(c => {
          outputVars.push(c);
        });
      });
      this.abbrev_to_var = {};
      outputVars.forEach(ov => {
        this.abbrev_to_var[ov.abbreviation] = ov;
      });

    this.dialog = ns;
    },
    getPvalColor(pv) {
      var c = colors['pvals'][pv.toString() + '-' + this.colorScheme];
      if (c) {
        return c['color'];
      } else {
        return 'white';
      }
    },
    pval_table_cell_aux(pval, which) {
      let ccl = this.colors['pvals']['1' + '-' + this.colorScheme][which];
      if (pval < 0.001) {
        ccl = this.colors['pvals']['0.001' + '-' + this.colorScheme][which];
      } else if (pval < 0.05) {
        ccl = this.colors['pvals']['0.05' + '-' + this.colorScheme][which];
      } else if (pval < 0.01) {
        ccl = this.colors['pvals']['0.01' + '-' + this.colorScheme][which];
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
    async saveCohorts(cohorts, cohortPrefix) {
      var nCohorts = cohorts.length;
      for (var c = nCohorts-1; c >= 0; c--) {
        const cohort = cohorts[c];
	var queries = {};
	queries[cohort.dimension] = [{"minValue": cohort.range.min * 1.0, "maxValue": cohort.range.max * 1.0}];
	var args = {
  	  name: cohortPrefix + cohort.label,
          collection: this.collection,
          queries: queries,
          inputVariables: this.inputVariables,
          outputVariables: this.outputVariables,
          subjectIds: cohort.subject_ids,
	};
	await this.saveCohort(args);
      }
      this.dialog = false;
    }
  },
};
</script>
