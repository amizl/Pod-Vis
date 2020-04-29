<template>
  <div>
    <v-data-table
      :headers="headers"
      :items="[...this.inputVariables].sort(this.scaleSortFn)"
      item-key="id"
      hide-actions
      dense
    >
      <template v-slot:items="props">
        <td style="font-size:0.9rem;">{{ props.item.category }}</td>
        <td style="font-size:0.9rem;">{{ props.item.label }}</td>
        <td>
          <v-checkbox
            v-model="props.item.inSelected"
            hide-details
            @change="masterCbChange(props.item)"
          ></v-checkbox>
        </td>
        <td>
          <v-checkbox
            v-if="props.item.has_first_and_last"
            v-model="props.item.children[0].inSelected"
            hide-details
            @change="cbChange"
          ></v-checkbox>
        </td>
        <td>
          <v-checkbox
            v-if="props.item.has_first_and_last"
            v-model="props.item.children[1].inSelected"
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
            v-model="props.item.children[2].inSelected"
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
            v-model="props.item.children[3].inSelected"
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
    inputVariables: [],
    propagateChanges: false,
  }),
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
  watch: {
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
