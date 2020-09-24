<template>
  <v-dialog v-model="openOutputVariableDialog" scrollable>
    <template v-slot:activator="{ on }">
      <v-btn text color="primary" class="title" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Choose Outcome Variables
      </v-btn>
    </template>
    <v-card class="rounded-lg">
      <v-card-title
        class="title primary--text text--darken-3"
        style="padding: 16px 16px 0px 16px;"
      >
        <div style="width: 100%; padding: 16px;">Choose Outcome Variables</div>
        <div style="width: 100%;">
          <v-data-table
            :items="sortScales([...this.outputVariables])"
            :headers="headers"
            item-key="id"
            hide-default-footer
            dense
            style="width: 100%;"
          >
            <template v-slot:item="props"> </template>
          </v-data-table>
        </div>
      </v-card-title>

      <v-card-text style="padding: 0px 16px 16px 16px;">
        <v-data-table
          :headers="headers"
          :items="sortScales([...this.outputVariables])"
          item-key="id"
          hide-default-header
          hide-default-footer
          dense
          disable-pagination
          style="width: 100%;"
        >
          <template v-slot:headers="props"> </template>
          <template v-slot:item="props">
            <tr>
              <td class="text-subtitle-1" style="width: 20%;">
                <v-row align="center">
                  <img
                    :src="'/images/' + props.item.category + '-icon-128.png'"
                    :title="props.item.category"
                    style="height:2em"
                    class="ma-1"
                  />
                  {{ props.item.category }}
                </v-row>
              </td>
              <td class="text-subtitle-1" style="width: 20%;">
                <v-tooltip top color="primary">
                  <template v-slot:activator="{ on: tooltip }">
                    <span v-on="{ ...tooltip }">
                      {{ props.item.abbreviation }}
                    </span>
                  </template>
                  <span v-html="props.item.label"></span>
                </v-tooltip>
              </td>
              <td class="text-subtitle-1" style="width 12%;">
                <v-simple-checkbox
                  v-model="props.item.outSelected"
                  hide-details
                  @input="masterCbChange(props.item)"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width 12%;">
                <v-simple-checkbox
                  v-if="props.item.has_first_and_last"
                  v-model="props.item.children[0].outSelected"
                  hide-details
                  @input="cbChange"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width 12%;">
                <v-simple-checkbox
                  v-if="props.item.has_first_and_last"
                  v-model="props.item.children[1].outSelected"
                  hide-details
                  @input="cbChange"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width 12%;">
                <v-simple-checkbox
                  v-if="
                    props.item.has_first_and_last &&
                      props.item.data_category !== 'Categorical'
                  "
                  v-model="props.item.children[2].outSelected"
                  hide-details
                  @input="cbChange"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width 12%;">
                <v-simple-checkbox
                  v-if="
                    props.item.has_first_and_last &&
                      props.item.data_category !== 'Categorical'
                  "
                  v-model="props.item.children[3].outSelected"
                  hide-details
                  @input="cbChange"
                ></v-simple-checkbox>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="openOutputVariableDialog = false"
          ><v-icon left dark>close</v-icon>Close</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { actions, state, getters } from '@/store/modules/cohortManager/types';
import { mapActions, mapState, mapGetters } from 'vuex';
import { uniqBy } from 'lodash';
import { sortScales } from '@/utils/helpers';

// traverse a list of variables and return the scale variables,
// which are either at or adjacent to the leaves
var getScaleVars = function(scaleVars, vars) {
  let has_first_and_last = false;

  vars.forEach(v => {
    if (v.children && v.children.length > 0) {
      // check whether the children are 'first visit', 'last visit', etc.
      if (v.children[0].label !== 'First Visit') {
        getScaleVars(scaleVars, v.children);
        return;
      } else {
        has_first_and_last = true;
      }
    }
    // include this variable
    if (!v.category) {
      v.category = v.label;
    }
    v.has_first_and_last = has_first_and_last;
    scaleVars.push(v);
  });
};

export default {
  props: {
    search: {
      type: String,
      default: '',
    },
  },
  data: () => ({
    searchVariable: '',
    openOutputVariableDialog: false,
    headers: [
      {
        text: 'Category',
        value: 'category',
        width: '20%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'Variable',
        value: 'label',
        width: '20%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'All',
        value: '',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'First Visit',
        value: '',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'Last Visit',
        value: '',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'Change',
        value: '',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'ROC',
        value: '',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
    ],
    outputVariables: [],
    observationVariablesD: {},
    propagateChanges: false,
    sortScales: sortScales,
  }),
  computed: {
    ...mapGetters('cohortManager', {
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      vars: state.OUTPUT_VARIABLES,
      cohort: state.COHORT,
    }),
  },

  watch: {
    openOutputVariableDialog(open) {
      // set flag to allow propagation of dialog changes back to UI
      this.propagateChanges = open;
      if (open) {
        this.$emit('dialogOpened', true);
      }
    },
    cohort() {
      this.updateOutputVars();
      let selectedVarsD = {};

      // pull vars from user-selected cohort
      if (this.hasUserSelectedCohort) {
        this.vars.forEach(v => {
          selectedVarsD[v.id] = true;
          if (v.children) {
            v.children.forEach(c => {
              selectedVarsD[c.id] = true;
            });
          }
        });

        // and reset everything else
        this.outputVariables.forEach(iv => {
          if (iv.children) {
            iv.children.forEach(cv => {
              var outSel = cv.id in selectedVarsD;
              if (cv.outSelected != outSel) {
                cv.outSelected = outSel;
              }
            });
          }
          var ivSel = iv.id in selectedVarsD;
          if (iv.outSelected != ivSel) iv.outSelected = ivSel;
        });
      }
    },
  },
  async created() {
    this.updateOutputVars();
  },
  methods: {
    ...mapActions('cohortManager', {
      setOutputVariables: actions.SET_OUTPUT_VARIABLES,
    }),

    updateOutputVars() {
      let vars = [];
      getScaleVars(vars, this.collection.observation_variables);
      this.outputVariables = vars;

      const obsD = this.observationVariablesD;
      const indexVars = function(vars) {
        vars.forEach(v => {
          obsD[v.id] = v;
          if (v.children) indexVars(v.children);
        });
      };
      indexVars(this.outputVariables);
    },

    updateSelectedVars() {
      let selectedOutputVars = [];
      this.outputVariables.forEach(iv => {
        if (iv.children && iv.children.length > 0) {
          let allSelected = true;
          iv.children.forEach(cv => {
            if (cv.outSelected) {
              selectedOutputVars.push(cv);
            } else if (
              cv.data_category != 'Categorical' ||
              (cv.label != 'Change' && cv.label != 'Rate of Change')
            ) {
              allSelected = false;
            }
          });
          iv.outSelected = allSelected;
        } else if (iv.outSelected) {
          selectedOutputVars.push(iv);
        }
      });
      if (this.propagateChanges) {
        let oVars = selectedOutputVars.sort(this.scaleSortFn);
        // First Visit, Change, etc
        const dimensions = oVars.filter(variable => !variable.children);
        // Parent measures
        let measures = {};
        const obsD = this.observationVariablesD;

        // Group dimensions by (actual) parent
        dimensions.forEach(d => {
          if (d.is_longitudinal) {
            const measure = d.id.split('-')[0];
            const actual_parent_id = d.id.split('-')[1];
            const parent = obsD[actual_parent_id];
            if (!(parent.id in measures)) {
              measures[parent.id] = parent;
              parent.selected_measures = {};
            }
            parent.selected_measures[measure] = 1;
          } else {
            measures[d.id] = d;
          }
        });
        const measures_list = Object.keys(measures).map(function(k) {
          return measures[k];
        });
        this.setOutputVariables(measures_list);
        this.$emit('userSelectedOutputVariables', true);
      }
    },

    masterCbChange(v) {
      // check/uncheck all child variables to match the master checkbox
      if (v.children) {
        v.children.forEach(c => {
          if (
            c.data_category != 'Categorical' ||
            (c.label != 'Change' && c.label != 'Rate of Change')
          ) {
            c.outSelected = v.outSelected;
          }
        });
      }
      this.$nextTick(() => this.updateSelectedVars());
    },

    cbChange(cb) {
      this.$nextTick(() => this.updateSelectedVars());
    },
  },
};
</script>

<style lang="css" scoped>
div.v-input {
  align-items: left;
  justify-content: left;
}
</style>
