<template>
  <v-dialog v-model="openInputVariableDialog" max-width="80%" scrollable>
    <template v-slot:activator="{ on }">
      <v-btn text color="primary" class="title" v-on="on">
        <v-icon left dark large class="pr-2">add_circle</v-icon>
        Choose Predictor Variables
      </v-btn>
    </template>
    <v-card class="rounded-lg">
      <v-card-title class="title primary--text text--darken-3 px-4 py-2">
        Choose Predictor Variables
        <v-spacer></v-spacer>
        <v-switch
          v-model="useLongScaleNamesSelect"
          label="Use long variable names"
          class="pa-0 ma-0"
          hide-details
        ></v-switch>
      </v-card-title>

      <v-card-text style="padding: 0px 16px 16px 16px;">
        <v-data-table
          :items="this.inputVariables"
          :headers="headers"
          item-key="id"
          hide-default-footer
          dense
          style="width: 100%;"
          class="blue-grey lighten-5 mt-3"
        >
          <template v-slot:item="props"> </template>
        </v-data-table>

        <v-data-table
          :items="this.inputVariables"
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

        <v-data-table
          :items="this.inputVariables"
          :headers="headers"
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
              <td class="text-subtitle-1" style="width: 12%;">
                <v-simple-checkbox
                  v-model="props.item.inmSelected"
                  hide-details
                  @input="masterCbChange(props.item)"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width: 12%;">
                <v-simple-checkbox
                  v-if="props.item.has_first_and_last"
                  v-model="props.item.children[0].inSelected"
                  hide-details
                  @input="cbChange"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width: 12%;">
                <v-simple-checkbox
                  v-if="props.item.has_first_and_last"
                  v-model="props.item.children[1].inSelected"
                  hide-details
                  @input="cbChange"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width: 12%;">
                <v-simple-checkbox
                  v-if="
                    props.item.has_first_and_last &&
                      props.item.data_category !== 'Categorical'
                  "
                  v-model="props.item.children[2].inSelected"
                  hide-details
                  @input="cbChange"
                ></v-simple-checkbox>
              </td>
              <td class="text-subtitle-1" style="width: 12%;">
                <v-simple-checkbox
                  v-if="
                    props.item.has_first_and_last &&
                      props.item.data_category !== 'Categorical'
                  "
                  v-model="props.item.children[3].inSelected"
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
        <v-btn color="primary" text @click="openInputVariableDialog = false"
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
import { logEvent } from '@/utils/logging';

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
    openInputVariableDialog: false,
    headers: [
      {
        text: 'Domain',
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
    inputVariables: [],
    propagateChanges: false,
    sortScales: sortScales,
  }),
  watch: {
    openInputVariableDialog(open) {
      // set flag to allow propagation of dialog changes back to UI
      this.propagateChanges = open;
      if (open) {
        this.$emit('dialogOpened', true);
      }
      logEvent(
        this.$gtag,
        null,
        null,
        'inputvars_' + (open ? 'open' : 'close'),
        'click',
        null
      );
    },
    useLongScaleNames(useLong) {
      logEvent(
        this.$gtag,
        null,
        null,
        'uselongscales_' + (useLong ? 'on' : 'off'),
        'click',
        null
      );
    },
    cohort(c) {
      this.updateInputVars();
    },
    vars(v) {
      let selectedVarsD = {};

      // pull vars from user-selected cohort
      this.vars.forEach(v => {
        selectedVarsD[v.id] = true;
      });

      // and reset everything else
      this.inputVariables.forEach(iv => {
        if (iv.children && iv.children.length > 0) {
          let allSelected = true;
          iv.children.forEach(cv => {
            cv.inSelected = cv.id in selectedVarsD;
            if (!cv.inSelected) allSelected = false;
          });
          iv.inmSelected = allSelected;
        } else {
          iv.inmSelected = iv.id in selectedVarsD;
        }
      });
      logEvent(
        this.$gtag,
        null,
        null,
        'inputvars_changed',
        'click',
        v.map(iv => iv.abbreviation).join(',')
      );
      this.updateColumnCheckboxes();
    },
  },
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      vars: state.INPUT_VARIABLES,
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
  async created() {
    this.updateInputVars();
    this.useLongScaleNamesSelect = this.useLongScaleNames;
  },
  methods: {
    ...mapActions('cohortManager', {
      setInputVariables: actions.SET_INPUT_VARIABLES,
      setUseLongScaleNames: actions.SET_USE_LONG_SCALE_NAMES,
    }),
    updateInputVars() {
      let vars = [];
      getScaleVars(vars, this.collection.subject_variables);
      getScaleVars(vars, this.collection.observation_variables);
      this.inputVariables = sortScales(vars);
    },
    updateSelectedVars() {
      let selectedInputVars = [];
      this.inputVariables.forEach(iv => {
        if (iv.children && iv.children.length > 0) {
          let allSelected = true;
          iv.children.forEach(cv => {
            if (cv.inSelected) {
              selectedInputVars.push(cv);
            } else if (
              cv.data_category != 'Categorical' ||
              (cv.label != 'Change' && cv.label != 'Rate of Change')
            ) {
              allSelected = false;
            }
          });
          if (iv.inmSelected != allSelected) iv.inmSelected = allSelected;
        } else if (iv.inmSelected) {
          selectedInputVars.push(iv);
        }
      });
      if (this.propagateChanges) {
        this.setInputVariables(selectedInputVars.sort(this.scaleSortFn));
        this.$emit('userSelectedInputVariables', true);
      }
      this.updateColumnCheckboxes();
    },

    // column master checkbox clicked
    columnCheckboxChange(which) {
      var cn = ['firstVisit', 'lastVisit', 'change', 'ROC'].findIndex(
        x => x == which
      );
      var vm = this;
      this.inputVariables.forEach(v => {
        if (which == 'all') {
          v.inmSelected = vm.columnCheckboxes['all'];
          vm.masterCbChange(v);
        } else if (cn != -1 && v.children && v.children.length > cn) {
          v.children[cn].inSelected = vm.columnCheckboxes[which];
        }
      });
      this.$nextTick(() => this.updateSelectedVars());
    },

    // update state of column master checkboxes based on the current state
    updateColumnCheckboxes() {
      var init = this.inputVariables && this.inputVariables.length > 0;
      var cbStates = {
        all: init,
        firstVisit: init,
        lastVisit: init,
        change: init,
        ROC: init,
      };
      this.inputVariables.forEach(v => {
        if (!v.inmSelected) {
          cbStates['all'] = false;
        }
        var i = 0;
        ['firstVisit', 'lastVisit', 'change', 'ROC'].forEach(m => {
          if (
            v.children &&
            v.children.length > i &&
            !v.children[i].inSelected
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

    // row master checkbox clicked
    masterCbChange(v) {
      // check/uncheck all child variables to match the master checkbox
      if (v.children) {
        v.children.forEach(c => {
          if (
            c.data_category != 'Categorical' ||
            (c.label != 'Change' && c.label != 'Rate of Change')
          ) {
            c.inSelected = v.inmSelected;
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
