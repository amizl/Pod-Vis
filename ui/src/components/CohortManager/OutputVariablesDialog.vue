<template>
  <v-dialog v-model="openOutputVariableDialog" scrollable>
    <template v-slot:activator="{ on }">
      <v-btn text color="primary" class="title" v-on="on">
        <v-icon left dark large class="pr-2">add_circle</v-icon>
        Choose Outcome Variables
      </v-btn>
    </template>
    <v-card class="rounded-lg">
      <v-card-title
        class="title primary--text text--darken-3"
        style="padding: 16px 16px 0px 16px;"
      >
        <div style="width: 100%; padding: 16px;">
          Choose Outcome Variables
          <v-switch
            v-model="useLongScaleNamesSelect"
            label="Use long scale names"
            class="pa-0 ma-0"
            hide-details
          ></v-switch>
        </div>
        <div style="width: 100%;">
          <v-data-table
            key="ovd-header"
            :items="this.outputVariables"
            :headers="headers"
            item-key="id"
            hide-default-footer
            dense
            style="width: 100%;"
            class="blue-grey lighten-5"
          >
            <template v-slot:item="props"> </template>
          </v-data-table>

          <v-data-table
            :items="this.outputVariables"
            :headers="headers"
            item-key="id"
            hide-default-footer
            dense
            style="width: 100%;"
            class="blue-grey lighten-5"
          >
            <template v-slot:header.category="{ header }"> </template>
            <template v-slot:header.label="{ header }"> </template>
            <template v-slot:header.all="{ header }">
              <v-simple-checkbox
                v-if="showAllVarsCheckbox"
                v-model="columnCheckboxes['all']"
                hide-details
                @input="columnCheckboxChange('all')"
              />
            </template>
            <template v-slot:header.fv="{ header }">
              <v-simple-checkbox
                v-model="columnCheckboxes['firstVisit']"
                hide-details
                @input="columnCheckboxChange('firstVisit')"
              />
            </template>
            <template v-slot:header.lv="{ header }">
              <v-simple-checkbox
                v-model="columnCheckboxes['lastVisit']"
                hide-details
                @input="columnCheckboxChange('lastVisit')"
              />
            </template>
            <template v-slot:header.ch="{ header }">
              <v-simple-checkbox
                v-model="columnCheckboxes['change']"
                hide-details
                @input="columnCheckboxChange('change')"
              />
            </template>
            <template v-slot:header.roc="{ header }">
              <v-simple-checkbox
                v-model="columnCheckboxes['ROC']"
                hide-details
                @input="columnCheckboxChange('ROC')"
              />
            </template>
            <template v-slot:item="props"> </template>
          </v-data-table>
        </div>
      </v-card-title>

      <v-card-text style="padding: 0px 16px 16px 16px;">
        <v-data-table
          key="ovd"
          :headers="headers"
          :items="this.outputVariables"
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
              <td class="text-subtitle-1" style="width 12%;">
                <v-simple-checkbox
                  v-model="props.item.outmSelected"
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
    showAllVarsCheckbox: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    // checkboxes to select all items in a column
    columnCheckboxes: {
      all: false,
      firstVisit: false,
      lastVisit: false,
      change: false,
      ROC: false,
    },
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
        value: 'all',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'First Visit',
        value: 'fv',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'Last Visit',
        value: 'lv',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'Change',
        value: 'ch',
        width: '12%',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      },
      {
        text: 'Rate of Change',
        value: 'roc',
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
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      vars: state.OUTPUT_VARIABLES,
      cohort: state.COHORT,
      useLongScaleNames: state.USE_LONG_SCALE_NAMES,
    }),
    useLongScaleNamesSelect: {
      get() {
        return this.useLongScaleNames;
      },
      set(value) {
        this.setUseLongScaleNames(value);
      },
    },
  },

  watch: {
    openOutputVariableDialog(open) {
      // set flag to allow propagation of dialog changes back to UI
      this.propagateChanges = open;
      if (open) {
        this.$emit('dialogOpened', true);
      }
    },
    cohort(c) {
      this.updateOutputVars();
    },
    vars(newvars) {
      let selectedVarsD = {};

      // pull vars from user-selected cohort
      newvars.forEach(v => {
        if (v.children && v.children.length > 0) {
          v.children.forEach(c => {
            if (!('outSelected' in c) || c.outSelected) {
              selectedVarsD[c.id] = true;
            }
          });
        } else {
          selectedVarsD[v.id] = true;
        }
      });

      // and reset everything else
      this.outputVariables.forEach(iv => {
        if (iv.children && iv.children.length > 0) {
          let allSelected = true;
          iv.children.forEach(cv => {
            var outSel = cv.id in selectedVarsD;
            if (cv.outSelected != outSel) {
              cv.outSelected = outSel;
            }
            if (!outSel) allSelected = false;
          });
          iv.outmSelected = allSelected;
        } else {
          var ivSel = iv.id in selectedVarsD;
          if (iv.outmSelected != ivSel) iv.outmSelected = ivSel;
        }
      });
    },
  },
  async created() {
    this.updateOutputVars();
    this.useLongScaleNamesSelect = this.useLongScaleNames;
  },
  methods: {
    ...mapActions('cohortManager', {
      setOutputVariables: actions.SET_OUTPUT_VARIABLES,
      setUseLongScaleNames: actions.SET_USE_LONG_SCALE_NAMES,
    }),

    updateOutputVars() {
      let vars = [];
      getScaleVars(vars, this.collection.observation_variables);
      this.outputVariables = sortScales(vars);

      const obsD = this.observationVariablesD;
      const indexVars = function(vars) {
        vars.forEach(v => {
          obsD[v.id] = v;
          if (!('inSelected' in v)) v.inSelected = false;
          if (!('outSelected' in v)) v.outSelected = false;
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
          if (iv.outmSelected != allSelected) iv.outmSelected = allSelected;
        } else if (iv.outmSelected) {
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
      this.updateColumnCheckboxes();
    },

    // column master checkbox clicked
    columnCheckboxChange(which) {
      var cn = ['firstVisit', 'lastVisit', 'change', 'ROC'].findIndex(
        x => x == which
      );
      var vm = this;
      this.outputVariables.forEach(v => {
        if (which == 'all') {
          v.outmSelected = vm.columnCheckboxes['all'];
          vm.masterCbChange(v);
        } else if (cn != -1 && v.children && v.children.length > cn) {
          v.children[cn].outSelected = vm.columnCheckboxes[which];
        }
      });
      this.$nextTick(() => this.updateSelectedVars());
    },

    // update state of column master checkboxes based on the current state
    updateColumnCheckboxes() {
      var cbStates = {
        all: true,
        firstVisit: true,
        lastVisit: true,
        change: true,
        ROC: true,
      };
      this.outputVariables.forEach(v => {
        if (!v.outmSelected) {
          cbStates['all'] = false;
        }
        var i = 0;
        ['firstVisit', 'lastVisit', 'change', 'ROC'].forEach(m => {
          if (
            v.children &&
            v.children.length > i &&
            !v.children[i].outSelected
          ) {
            cbStates[m] = false;
          }
          i += 1;
        });
      });
      var vm = this;
      Object.keys(cbStates).forEach(k => {
        if (vm.columnCheckboxes[k] != cbStates[k])
          vm.columnCheckboxes[k] = cbStates[k];
      });
    },

    masterCbChange(v) {
      // check/uncheck all child variables to match the master checkbox
      if (v.children) {
        v.children.forEach(c => {
          if (
            c.data_category != 'Categorical' ||
            (c.label != 'Change' && c.label != 'Rate of Change')
          ) {
            c.outSelected = v.outmSelected;
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
