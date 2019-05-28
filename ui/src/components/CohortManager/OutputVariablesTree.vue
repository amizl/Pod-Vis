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
    selectedObservationVariables: [],
    dragging: false,
    hovering: false,
    observationVariables: [],
  }),
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
    }),
  },
  watch: {
    selectedObservationVariables(newObservationVariable) {
      this.setOutputVariables(
        newObservationVariable.filter(variable => !variable.children)
      );
    },
  },
  async created() {
    const observationVariables = this.makeHierarchy(
      this.collection.observation_variables
    );

    observationVariables.forEach(observationVariable => {
      observationVariable.children.forEach(
        child => (child['type'] = 'observation')
      );
    });

    this.observationVariables = observationVariables;
  },
  methods: {
    ...mapActions('cohortManager', {
      setOutputVariables: actions.SET_OUTPUT_VARIABLES,
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
