<template>
  <v-sheet color="white" height="100%" class="scroll rounded-lg shadow">
    <v-card-title class="title primary--text">Outcome Variables</v-card-title>
    <v-divider></v-divider>
    <v-card-text class="">
      <v-treeview
        v-model="selectedObservationVariables"
        color="primary"
        selectable
        return-object
        :items="observationVariables"
        item-text="label"
      ></v-treeview>
    </v-card-text>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';

export default {
  data() {
    return {
      selectedObservationVariables: [],
      observationVariables: [],
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      collection: state.COLLECTION,
    }),
  },
  watch: {
    selectedObservationVariables(newObservationVariables) {
      // SCOPA, UPDRS, etc
      const outcomeMeasures = newObservationVariables.filter(
        variable => variable.parent_id != 1
      );

      this.setOutcomeVariables(outcomeMeasures);
    },
  },
  async created() {
    this.observationVariables = this.collection.observation_variables;
  },
  mounted() {
    // console.log(this.$refs.container.getBoundingClientRect());
  },
  methods: {
    ...mapActions('dataExplorer', {
      setOutcomeVariables: actions.SET_OUTCOME_VARIABLES,
    }),
  },
};
</script>

<style scoped></style>
