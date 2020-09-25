<template>
  <v-sheet class="ma-1 pa-0" color="white" height="100%" min-width="400px">
    <v-container fluid fill-width class="pa-0 ma-0">
      <!-- Variable icon/title/reset button -->
      <v-row class="pa-0 ma-0" :class="getTitleClass(variable) + ' pt-1'">
        <v-col cols="12" class="pa-0 ma-0">
          <v-container class="pa-0 ma-0">
            <v-row class="pa-0 ma-0">
              <v-col cols="2" class="pa-0 ma-0 pl-2 pt-1">
                <span>
                  <img
                    :src="'/images/' + variable.category + '-icon-128.png'"
                    :title="variable.category"
                    style="height: 3em;"
                  />
                </span>
              </v-col>

              <v-col cols="7" class="pa-0 ma-0 pt-0">
                <div class="text-h6 ml-2 text-wrap">
                  <v-tooltip top color="primary">
                    <template v-slot:activator="{ on: tooltip }">
                      <span v-on="{ ...tooltip }">
                        {{ getVariableAbbreviation(variable) }}
                      </span>
                    </template>
                    <span>{{ getVariableLabel(variable) }}</span>
                  </v-tooltip>
                </div>
              </v-col>

              <v-col cols="3" class="pa-0 ma-0 pt-2 pr-2" align="right">
                <span>
                  <v-btn
                    outlined
                    medium
                    class="together primary--text text--lighten-3 ma-0 pa-0 ml-2"
                    @click="resetClicked"
                  >
                    Reset
                  </v-btn>
                </span>
              </v-col>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
      <!-- End of Variable icon/title/reset button -->
    </v-container>

    <v-container fluid fill-width class="pa-0 ma-0">
      <v-row class="pa-0 ma-0">
        <v-col cols="12" class="pa-0 ma-0">
          <div v-if="variable.value_type === 'date'" class="pl-3">
            Date types not supported.
          </div>
          <ColumnChart
            v-else-if="
              variable.is_longitudinal === false &&
                variable.data_category === 'Categorical'
            "
            :id="variable.id"
            :key="'ovcc-' + variable.id"
            :dimension-name="variable.label"
            @userChangedVariable="userChangedOutputVariable"
          />
          <HistogramChart
            v-else-if="variable.is_longitudinal === false"
            :id="variable.id"
            :key="'ovhc-' + variable.id"
            :dimension-name="variable.label"
            :input-variable="false"
            :variable="variable"
            @userChangedVariable="userChangedOutputVariable"
          />
          <MultiChart
            v-else
            :key="'ovmc-' + variable.id + '-' + getSelectedMeasuresKey(variable)"
            class="ma-1"
            :variable="variable"
            :dimension-name="dimension"
            :highlight-change="isBelowPValThreshold(variable)"
            :first-visit-label="getFirstVisitLabel()"
            :last-visit-label="getLastVisitLabel()"
            width="400px"
            @userChangedVariable="userChangedOutputVariable"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
</template>

<script>
import ColumnChart from '@/components/CohortManager/BarChart/BarChart.vue';
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';
import MultiChart from '@/components/CohortManager/MultiChart.vue';
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  components: {
    ColumnChart,
    HistogramChart,
    MultiChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return { dimension: null, resetCount: 0 };
  },
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      pvals: state.PVALS,
      pval_threshold: state.PVAL_THRESHOLD,
      dimensions: state.DIMENSIONS,
    }),
  },
  created() {
    if (this.variable.children) {
      this.variable.children.forEach(childVariable => {
        this.addDimensionHelper(childVariable);
      });
      this.dimension = this.variable.id;
    } else {
      this.addDimensionHelper(this.variable);
    }
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
      clearFilter: actions.CLEAR_FILTER,
    }),
    resetClicked() {
      this.clearAllFilters();
      this.$emit('userResetOutputVariable', this.dimension);
    },
    userChangedOutputVariable() {
      this.$emit('userChangedOutputVariable', this.dimension);
    },
    clearAllFilters() {
      this.clearFilter({ dimension: this.variable.label });
      // cover all the bases for the MultiChart/longitudinal case
      this.clearFilter({ dimension: this.variable.label + ' - First Visit' });
      this.clearFilter({ dimension: this.variable.label + ' - Last Visit' });
      this.clearFilter({ dimension: this.variable.label + ' - Change' });
      this.clearFilter({
        dimension: this.variable.label + ' - Rate of Change',
      });
    },
    addDimensionHelper(variable) {
      var measure = null;
      var dimensionName = null;
      var dimensionId = null;

      if (variable.is_longitudinal) {
        measure = variable.id.split('-')[0];
        dimensionName = `${variable.parentLabel} - ${variable.label}`;
        dimensionId = variable.parentID;
      } else {
        measure = 'value';
        dimensionName = variable.label;
        dimensionId = variable.id;
      }
      this.dimension = String(dimensionId).toString();

      const payload = {
        dimensionName,
        accessor: d => {
          const dimName = dimensionId;
          return d[dimName][measure];
        },
      };
      this.addDimension(payload);
    },
    isBelowPValThreshold(v) {
      const pvt = this.pval_threshold;
      let rv = false;
      if (!this.pvals) {
        return false;
      }
      this.pvals.forEach(pv => {
        if (
          pv.label === v.label ||
          (pv.label === v.parentLabel && v.label === 'Change')
        ) {
          if (pv.pval < pvt) {
            rv = true;
          }
        }
      });
      return rv;
    },
    getTitleClass(v) {
      const dflt =
        'subheading primary--text text--darken-4 pa-0 ma-0 text-truncate';
      if (this.isBelowPValThreshold(v)) {
        return `${dflt} highlight-var`;
      }
      return `${dflt} not-highlight-var`;
    },
    getOutcomeClass(v) {
      if (this.isBelowPValThreshold(v)) {
        return 'highlight-var-chart';
      }
      return 'var-chart';
    },
    getVariableAbbreviation(v) {
      if (v.parentLabel) {
        return `${v.parentLabel} - ${v.abbreviation}`;
      }
      return v.abbreviation;
    },
    getVariableLabel(v) {
      if (v.parentLabel) {
        return `${v.parentLabel} - ${v.label}`;
      }
      return v.label;
    },
    getVisitLabel(isFirst) {
      var which = isFirst ? 'first' : 'last';
      var result = '?';
      this.collection.observation_variables_list.forEach(ov => {
        if (ov.ontology.id == this.variable.id) {
          if (ov[which + '_visit_event']) {
            result = String(ov[which + '_visit_event']);
          } else {
            result = String(ov[which + '_visit_num']);
          }
        }
      });
      return result;
    },
    getFirstVisitLabel() {
      return this.getVisitLabel(true);
    },
    getLastVisitLabel() {
      return this.getVisitLabel(false);
    },
    getSelectedMeasuresKey(v) {
      var key = "";
      if (!('selected_measures' in v)) {
        return "all";
      }

      ["firstVisit", "lastVisit", "change", "roc"].forEach(m => {
        if ((m in v['selected_measures']) && v['selected_measures'][m]) {
          key += "1";
        } else {
          key += "0";
        }
      });
    return key;
    }
  },
};
</script>

<style lang="scss" scoped></style>
