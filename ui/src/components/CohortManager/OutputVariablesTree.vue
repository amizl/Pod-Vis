<template>
  <v-treeview
    v-model="selectedObservationVariables"
    color="primary"
    selectable
    return-object
    :items="observationVariables"
    :search="search"
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
          v.children.forEach(c => {
            if (c.type === 'observation') {
              selectedVars.push(c);
            }
          });
        });
        this.selectedObservationVariables = selectedVars;
      }
      // otherwise reset selections
      else {
        this.selectedObservationVariables = [];
      }
    },
    selectedObservationVariables(newObservationVariables) {
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
           const measure = d.id.split('-')[0];
           const actual_parent_id = d.id.split('-')[1];
           const parent = obsD[actual_parent_id];
           if (!(parent.id in measures)) {
             measures[parent.id] = parent;
             parent.selected_measures = {};
           }
           parent.selected_measures[measure] = 1;
         });

         const measures_list = Object.keys(measures).map(function(k) {return measures[k]});
         this.setOutputVariables(measures_list);
      }
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
  },
};
</script>

<style lang="scss" scoped></style>
