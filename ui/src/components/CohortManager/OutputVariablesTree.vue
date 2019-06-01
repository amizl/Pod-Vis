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
