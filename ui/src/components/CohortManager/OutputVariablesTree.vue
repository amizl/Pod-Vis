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
        // SCOPA, UPDRS, etc
        const outcomeMeasures = newObservationVariables.filter(
          variable =>
            variable.children &&
            variable.children.length &&
            'data_category' in variable &&
            variable.parent_id !== 1
        );

        // First Visit, Change, etc
        const dimensions = newObservationVariables.filter(
          variable => !variable.children
        );

        // If a user selected a study with all of its dimensions,
        // we want to add just the one study and remove dimensions
        // so we can draw a parallel coordinates plot
        const parentIDs = outcomeMeasures.map(m => m.id);
        const dimensionsNotInParentIDs = dimensions.filter(
          obs => !parentIDs.includes(obs.parentID)
        );

        this.setOutputVariables(
          [...outcomeMeasures, ...dimensionsNotInParentIDs]
          // newObservationVariables.filter(variable => !variable.children)
        );
      }
    },
  },
  async created() {
    this.observationVariables = this.collection.observation_variables;
  },
  methods: {
    ...mapActions('cohortManager', {
      setOutputVariables: actions.SET_OUTPUT_VARIABLES,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
