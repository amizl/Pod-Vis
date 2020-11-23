<template>
  <v-sheet color="white" height="100%" min-width="380px" max-width="500px">
    <v-container fluid fill-width class="pa-0 ma-0">
      <!-- Variable icon/title/reset button -->
      <v-row class="pa-0 ma-0">
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
                        {{ getChartTitle(variable, 'abbreviation') }}
                      </span>
                    </template>
                    <span>{{ getChartTitle(variable, 'label') }}</span>
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
              (!variable.is_longitudinal &&
                variable.data_category === 'Categorical') ||
                variable.type === 'study'
            "
            :id="variable.id"
            :dimension-name="dimension"
            show-selection
            bar-tooltip="Click to add or remove this value from the cohort filter"
            @userChangedVariable="userChangedInputVariable"
          />
          <HistogramChart
            v-else-if="variable.data_category !== 'Categorical'"
            :id="variable.id"
            :dimension-name="dimension"
            :variable="variable"
            input-variable
            @userChangedVariable="userChangedInputVariable"
          />
          <ColumnChart
            v-else
            :id="variable.id"
            :dimension-name="dimension"
            show-selection
            @userChangedVariable="userChangedInputVariable"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
</template>
columnchar
<script>
import ColumnChart from '@/components/CohortManager/BarChart/BarChart.vue';
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';

export default {
  components: {
    ColumnChart,
    HistogramChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
    useLongScaleNames: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return { dimension: null };
  },
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      dimensions: state.DIMENSIONS,
      unfilteredData: state.UNFILTERED_DATA,
    }),
  },
  created() {
    this.addDimensionHelper(this.variable);
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
      clearFilter: actions.CLEAR_FILTER,
    }),
    resetClicked() {
      this.clearFilter({ dimension: this.dimension });
      this.$emit('userResetInputVariable', this.dimension);
    },
    userChangedInputVariable() {
      this.$emit('userChangedInputVariable', this.dimension);
    },
    getChartTitle(v, which) {
      var title = null;
      if (which == 'abbreviation') {
        title = this.useLongScaleNames ? v.label : v.abbreviation;
      } else {
        title = this.useLongScaleNames ? v.description : v.label;
      }

      if (v.type == 'observation' && v.is_longitudinal) {
        var fv = null;
        var lv = null;
        var p_name = null;

        this.collection.observation_variables_list.forEach(ov => {
          if (ov.ontology.id == v.parentID) {
            if (ov['first_visit_event']) {
              fv = ov['first_visit_event'];
              lv = ov['last_visit_event'];
              p_name = ov['ontology'][which];
            } else {
              fv = ov['first_visit_num'];
              lv = ov['last_visit_num'];
              p_name = ov['ontology'][which];
            }
          }
        });
        if (v.label == 'First Visit') {
          title = p_name + ' - ' + (which == 'label' ? 'Visit=' : '') + fv;
        } else if (this.variable.label == 'Last Visit') {
          title = p_name + ' - ' + (which == 'label' ? 'Visit=' : '') + lv;
        } else {
          var label = v.label;
          if (label == 'Rate of Change' && which == 'abbreviation') {
            label = 'Rate of Change';
          }

          title = p_name + ' - ' + label + ': ' + fv + '-' + lv;
        }
      }
      return title;
    },
    addDimensionHelper(variable) {
      var dimensionName = null;
      var payload = null;

      // observation variable
      if (this.variable.type === 'observation') {
        var dimensionId = null;
        var measure = null;

        if (variable.is_longitudinal) {
          measure = this.variable.id.split('-')[0];
          dimensionName = `${this.variable.parentLabel} - ${
            this.variable.label
          }`;
          dimensionId = this.variable.parentID;
        } else {
          measure = 'value';
          dimensionName = variable.label;
          dimensionId = variable.id;
        }
        payload = {
          dimensionName,
          accessor: d => {
            const dimName = dimensionId;
            return d[dimName][measure];
          },
        };
      }
      // subject variable
      else {
        if (
          this.variable.label === 'Study' ||
          this.variable.label === 'Dataset'
        ) {
          dimensionName = this.variable.label;
          payload = {
            dimensionName: dimensionName,
            accessor: d => d.study.study_name,
          };
        } else {
          dimensionName = this.variable.label;
          payload = {
            dimensionName: dimensionName,
            accessor: d => {
              const dimName = dimensionName;
              return d[dimName];
            },
          };
        }
      }
      this.dimension = dimensionName;
      this.addDimension(payload);
    },
  },
};
</script>

<style lang="scss" scoped></style>
