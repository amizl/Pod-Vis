<template>
  <div>
    <v-treeview
      v-model="selectedSubjectVariables"
      color="primary"
      return-object
      selectable
      :search="search"
      :items="subjectVariables"
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
    }),
  },
  watch: {
    selectedSubjectVariables(newSubjectVariables) {
      this.setInputVariables([
        // Filter parent nodes because we don't want them added to our list,
        // i.e, 'Demographics'
        ...newSubjectVariables.filter(variable => !variable.children),
        ...this.selectedObservationVariables,
      ]);
    },
    selectedObservationVariables(newObservationVariable) {
      this.setInputVariables([
        ...this.selectedSubjectVariables,
        ...newObservationVariable.filter(variable => !variable.children),
      ]);
    },
    collection() {
      // const subjectVariables = this.makeH ierarchy(
      //   this.collection.subject_variables.map(variable => ({
      //     ...variable,
      //     type: 'subject',
      //   }))
      // );

      const subjectVariables = this.makeHierarchy(
        this.collection.subject_variables
      );
      subjectVariables.forEach(subjectVariable => {
        subjectVariable.children.forEach(child => (child['type'] = 'subject'));
      });

      const observationVariables = this.makeHierarchy(
        this.collection.observation_variables
      );

      observationVariables.forEach(observationVariable => {
        observationVariable.children.forEach(
          child => (child['type'] = 'observation')
        );
      });

      this.subjectVariables = subjectVariables;
      this.observationVariables = observationVariables;
    },
  },
  async created() {
    // console.log(this.collection.observation_variables);
    // console.log(this.collection.subject_variables);
    // fetch the shared input and output variables for collection
    // and assign them to variables...
  },
  methods: {
    ...mapActions('cohortManager', {
      setInputVariables: actions.SET_INPUT_VARIABLES,
    }),
    fetchVariables() {
      // fetch the shared input and output variables for collection
    },
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
