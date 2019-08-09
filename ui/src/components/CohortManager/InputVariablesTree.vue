<template>
  <div>
    <v-treeview
      v-model="selectedSubjectVariables"
      color="primary"
      return-object
      selectable
      :search="search"
      :items="[
        { type: 'study', id: 'study_id', label: 'Study' },
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
import { actions, state } from '@/store/modules/cohortManager/types';
import { mapActions, mapState } from 'vuex';
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
  }),
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      vars: state.INPUT_VARIABLES,
    }),
  },
  watch: {
    selectedSubjectVariables(newSubjectVariables) {
      this.setInputVariables([
        // Filter parent nodes because we don't want them added to our list,
        // i.e, 'Demographics'
        ...newSubjectVariables.filter(variable => !variable.children),
        ...this.selectedObservationVariables.filter(
          variable => !variable.children
        ),
      ]);
    },
    selectedObservationVariables(newObservationVariable) {
      this.setInputVariables([
        ...this.selectedSubjectVariables.filter(variable => !variable.children),
        ...newObservationVariable.filter(variable => !variable.children),
      ]);
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
