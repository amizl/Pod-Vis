<template>
  <div>
    <v-treeview
      v-model="selectedSubjectVariables"
      color="primary"
      return-object
      selectable
      :search="search"
      :items="[
        { type: 'study', id: 12, label: 'Study' },
        ...subjectVariables,
      ]"
      item-text="label"
    ></v-treeview>
    <v-treeview
      v-model="selectedObservationVariables"
      color="primary"
      selectable
      return-object
      :items="observationVariables"
      :search="search"
      item-text="label"
    ></v-treeview>
  </div>
</template>

<script>
import { actions, state, getters } from '@/store/modules/cohortManager/types';
import { mapActions, mapState, mapGetters } from 'vuex';
import { uniqBy } from 'lodash';

export default {
  props: {
    search: {
      type: String,
      default: '',
    },
  },
  data: () => ({
    selectedSubjectVariables: [],
    selectedObservationVariables: [],
    dragging: false,
    hovering: false,
    observationVariables: [],
    subjectVariables: [],
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
       // pull vars from user-selected cohort
       if (this.hasUserSelectedCohort) {
        this.selectedSubjectVariables = this.vars.filter(
          variable => variable.type === 'subject'
        );
        this.selectedObservationVariables = this.vars.filter(
          variable => variable.type === 'observation'
        );
      }
      // otherwise reset selections
      else {
        this.selectedSubjectVariables = [];
        this.selectedObservationVariables = [];
      }
      // const observationVariables = newCohort.input_variables
      //   .filter(variable => variable.observation_ontology !== null)
      //   .map(variable => variable.observation_ontology.id);
    },
    selectedSubjectVariables(newSubjectVariables) {
      if (this.propagateChanges) {
        this.setInputVariables([
          // Filter parent nodes because we don't want them added to our list,
          // i.e, 'Demographics'
          ...newSubjectVariables.filter(variable => !variable.children),
          ...this.selectedObservationVariables.filter(
            variable => !variable.children
          ),
        ]);
      }
    },
    selectedObservationVariables(newObservationVariable) {
      if (this.propagateChanges) {
        this.setInputVariables([
          ...this.selectedSubjectVariables.filter(
            variable => !variable.children
          ),
          ...newObservationVariable.filter(variable => !variable.children),
        ]);
      }
    },
  },
  async created() {
    this.subjectVariables = this.collection.subject_variables;
    this.observationVariables = this.collection.observation_variables;
  },
  methods: {
    ...mapActions('cohortManager', {
      setInputVariables: actions.SET_INPUT_VARIABLES,
    }),
    makeHierarchy(data) {
      const ontologies = data.map(obs => obs.ontology);
      const parents = uniqBy(
        ontologies.map(ontology => ontology.parent),
        'label'
      ).map(parent => ({
        ...parent,
        children: ontologies.filter(
          ontology => ontology.parent.label === parent.label
        ),
      }));
      return parents;
    },
  },
};
</script>

<style lang="scss" scoped></style>
