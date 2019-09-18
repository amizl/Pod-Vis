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
        var selected_vars = [];
        this.vars.forEach(function(v) {
          v.children.forEach(function(c) {
            if (c.type === 'observation') {
              selected_vars.push(c);
            }
          });
	});
        this.selectedObservationVariables = selected_vars;
      }
      // otherwise reset selections
      else {
        this.selectedObservationVariables = [];
      }
    },
    selectedObservationVariables(newObservationVariables) {
      if (!this.hasUserSelectedCohort) {
        // SCOPA, UPDRS, etc
        const outcomeMeasures = newObservationVariables.filter(
          variable =>
            variable.children &&
            variable.children.length &&
            variable.parent_id != 1
        );
        // Fist Visit, Change, etc
        const dimensions = newObservationVariables.filter(
          variable => !variable.children
        );

        // If a user selected a study with all of its dimensions,
        // we want add just the one study and remove dimensions
        // so we can draw a parallel coordinates plot
        const parentIDs = outcomeMeasures.map(m => m.id);
        let dimensionsNotInParentIDs = dimensions.filter(
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
