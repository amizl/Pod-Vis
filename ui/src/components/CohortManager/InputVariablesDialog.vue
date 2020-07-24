<template>
  <v-dialog v-model="openInputVariableDialog" scrollable>
    <template v-slot:activator="{ on }">
      <v-btn text color="primary" class="title" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Choose Predictor Variables
      </v-btn>
    </template>
    <v-card class="rounded-lg">
      <v-card-title
        class="title primary--text text--darken-3"
        style="padding: 16px 16px 0px 16px;"
      >
        <div style="width: 100%; padding: 16px;">
          Choose Predictor Variables
        </div>
        <div style="width: 100%;">
          <v-data-table
            :items="[...this.inputVariables].sort(this.scaleSortFn)"
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
          :items="[...this.inputVariables].sort(this.scaleSortFn)"
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
              <td style="font-size:0.9rem; width: 20%;">
                {{ props.item.category }}
              </td>
              <td style="font-size:0.9rem; width: 20%;">
                {{ props.item.label }}
              </td>
              <td style="width: 12%;">
                <v-checkbox
                  v-model="props.item.inSelected"
                  hide-details
                  @change="masterCbChange(props.item)"
                ></v-checkbox>
              </td>
              <td style="width: 12%;">
                <v-checkbox
                  v-if="props.item.has_first_and_last"
                  v-model="props.item.children[0].inSelected"
                  hide-details
                  @change="cbChange"
                ></v-checkbox>
              </td>
              <td style="width: 12%;">
                <v-checkbox
                  v-if="props.item.has_first_and_last"
                  v-model="props.item.children[1].inSelected"
                  hide-details
                  @change="cbChange"
                ></v-checkbox>
              </td>
              <td style="width: 12%;">
                <v-checkbox
                  v-if="
                    props.item.has_first_and_last &&
                      props.item.data_category !== 'Categorical'
                  "
                  v-model="props.item.children[2].inSelected"
                  hide-details
                  @change="cbChange"
                ></v-checkbox>
              </td>
              <td style="width: 12%;">
                <v-checkbox
                  v-if="
                    props.item.has_first_and_last &&
                      props.item.data_category !== 'Categorical'
                  "
                  v-model="props.item.children[3].inSelected"
                  hide-details
                  @change="cbChange"
                ></v-checkbox>
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
    openInputVariableDialog: false,
    scaleSortFn: function(a, b) {
      return a.label < b.label ? -1 : a.label > b.label ? 1 : 0;
    },
    headers: [
      { text: 'Category', value: 'category', width: '20%', sortable: false },
      { text: 'Variable', value: 'label', width: '20%', sortable: false },
      { text: 'All', value: '', width: '12%', sortable: false },
      { text: 'First Visit', value: '', width: '12%', sortable: false },
      { text: 'Last Visit', value: '', width: '12%', sortable: false },
      { text: 'Change', value: '', width: '12%', sortable: false },
      { text: 'ROC', value: '', width: '12%', sortable: false },
    ],
    inputVariables: [],
    propagateChanges: false,
  }),
  watch: {
    openInputVariableDialog(open) {
      // set flag to allow propagation of dialog changes back to UI
      this.propagateChanges = open;
      if (open) {
        this.$emit('dialogOpened', true);
      }
    },
    cohort() {
      this.updateInputVars();
      let selectedVarsD = {};

      // pull vars from user-selected cohort
      if (this.hasUserSelectedCohort) {
        this.vars.forEach(v => {
          selectedVarsD[v.id] = true;
        });
      }

      // and reset everything else
      this.inputVariables.forEach(iv => {
        if (iv.children) {
          iv.children.forEach(cv => {
            cv.inSelected = cv.id in selectedVarsD;
          });
        }

        iv.inSelected = iv.id in selectedVarsD;
      });
    },
  },
  computed: {
    ...mapGetters('cohortManager', {
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      vars: state.INPUT_VARIABLES,
      cohort: state.COHORT,
    }),
  },
  async created() {
    this.updateInputVars();
  },
  methods: {
    ...mapActions('cohortManager', {
      setInputVariables: actions.SET_INPUT_VARIABLES,
    }),
    updateInputVars() {
      let vars = [];
      getScaleVars(vars, this.collection.subject_variables);
      getScaleVars(vars, this.collection.observation_variables);
      this.inputVariables = vars;
    },
    updateSelectedVars() {
      let selectedInputVars = [];
      this.inputVariables.forEach(iv => {
        if (iv.children && iv.children.length > 0) {
          let allSelected = true;
          iv.children.forEach(cv => {
            if (cv.inSelected) {
              selectedInputVars.push(cv);
            } else {
              allSelected = false;
            }
          });
          iv.inSelected = allSelected;
        } else if (iv.inSelected) {
          selectedInputVars.push(iv);
        }
      });
      if (this.propagateChanges) {
        this.setInputVariables(selectedInputVars.sort(this.scaleSortFn));
        // workaround for v-checkboxes not always updating correctly
        this.$forceUpdate();
      }
    },

    masterCbChange(v) {
      // check/uncheck all child variables to match the master checkbox
      if (v.children) {
        v.children.forEach(c => {
          c.inSelected = v.inSelected;
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
