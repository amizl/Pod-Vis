<template>
  <v-treeview
    v-model="selectedObservationVariables"
    color="primary"
    selectable
    return-object
    :items="observationVariables"
    :search="search"
    :open.sync="openObs"
    item-text="label"
  ></v-treeview>
</template>

<script>
import { actions, state, getters } from '@/store/modules/cohortManager/types';
import { mapActions, mapState, mapGetters } from 'vuex';

export default {
  props: {
    search: {
      type: String,
      default: '',
    },
  },
  data: () => ({
    selectedObservationVariables: [],
    dragging: false,
    hovering: false,
    observationVariables: [],
    observationVariablesD: [],
    propagateChanges: false,
    openObs: [],
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
      // pull vars from user-selected cohort
      if (this.hasUserSelectedCohort) {
        const selectedVars = [];
        this.vars.forEach(v => {
          if (!('children' in v)) {
            selectedVars.push(v);
          } else {
            v.children.forEach(c => {
              if (c.type === 'observation') {
                selectedVars.push(c);
              }
            });
          }
        });
        this.selectedObservationVariables = selectedVars;
      }
      // otherwise reset selections
      else {
        this.selectedObservationVariables = [];
      }
    },
    selectedObservationVariables(newObservationVariables) {
      var ovt = this;

      new Promise(function(resolve, reject) {
        // open up any selected nodes that are not already open
        var openIds = {};
        ovt.openObs.forEach(s => {
          openIds[s.id] = true;
        });
        newObservationVariables.forEach(s => {
          if (!(s.id in openIds)) {
            ovt.openObs.push(s);
          }
        });

        // slight delay on actually adding the variables so that the
        // dialog/tree has time to update first
        setTimeout(() => {
          ovt.observationVariablesChanged(newObservationVariables);
          resolve();
        }, 100);
      });
    },
  },
  async created() {
    this.observationVariables = this.collection.observation_variables;
    // recursively index observationVariables by id
    const obsD = this.observationVariablesD;
    const indexVars = function(vars) {
      vars.forEach(v => {
        obsD[v.id] = v;
        if (v.children) indexVars(v.children);
      });
    };
    indexVars(this.observationVariables);
  },
  methods: {
    ...mapActions('cohortManager', {
      setOutputVariables: actions.SET_OUTPUT_VARIABLES,
    }),
    observationVariablesChanged(newObservationVariables) {
      if (this.propagateChanges) {
        // First Visit, Change, etc
        const dimensions = newObservationVariables.filter(
          variable => !variable.children
        );

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
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
