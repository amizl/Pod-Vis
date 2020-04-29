<template>
  <div>
    <v-data-table
      :headers="headers"
      :items="[...this.outputVariables].sort(this.scaleSortFn)"
      item-key="id"
      hide-actions
      dense
    >
      <template v-slot:items="props">
        <td style="font-size:0.9rem;">{{ props.item.category }}</td>
        <td style="font-size:0.9rem;">{{ props.item.label }}</td>
        <td>
          <v-checkbox
            v-model="props.item.outSelected"
            hide-details
            @change="masterCbChange(props.item)"
          ></v-checkbox>
        </td>
        <td>
          <v-checkbox
            v-if="props.item.has_first_and_last"
            v-model="props.item.children[0].outSelected"
            hide-details
            @change="cbChange"
          ></v-checkbox>
        </td>
        <td>
          <v-checkbox
            v-if="props.item.has_first_and_last"
            v-model="props.item.children[1].outSelected"
            hide-details
            @change="cbChange"
          ></v-checkbox>
        </td>
        <td>
          <v-checkbox
            v-if="
              props.item.has_first_and_last &&
                props.item.data_category !== 'Categorical'
            "
            v-model="props.item.children[2].outSelected"
            hide-details
            @change="cbChange"
          ></v-checkbox>
        </td>
        <td>
          <v-checkbox
            v-if="
              props.item.has_first_and_last &&
                props.item.data_category !== 'Categorical'
            "
            v-model="props.item.children[3].outSelected"
            hide-details
            @change="cbChange"
          ></v-checkbox>
        </td>
      </template>
    </v-data-table>
  </div>
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
    scaleSortFn: function(a, b) {
      return a.label < b.label ? -1 : a.label > b.label ? 1 : 0;
    },
    headers: [
      { text: 'Category', value: 'category' },
      { text: 'Variable', value: 'label' },
      { text: 'All', value: '' },
      { text: 'First Visit', value: '' },
      { text: 'Last Visit', value: '' },
      { text: 'Change', value: '' },
      { text: 'Rate of Change', value: '' },
    ],
    outputVariables: [],
    observationVariablesD: {},
    propagateChanges: false,
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
      }

      // and reset everything else
      this.outputVariables.forEach(iv => {
        if (iv.children) {
          iv.children.forEach(cv => {
            cv.outSelected = cv.id in selectedVarsD;
          });
        }

        iv.outSelected = iv.id in selectedVarsD;
      });
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
            } else {
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

        //        this.setOutputVariables(oVars);
        // workaround for v-checkboxes not always updating correctly
        this.$forceUpdate();
      }
    },

    masterCbChange(v) {
      // check/uncheck all child variables to match the master checkbox
      if (v.children) {
        v.children.forEach(c => {
          c.outSelected = v.outSelected;
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
