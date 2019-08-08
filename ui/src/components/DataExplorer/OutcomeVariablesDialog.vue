<template>
  <v-dialog v-model="openInputVariableDialog" scrollable max-width="600px">
    <template v-slot:activator="{ on }">
      <v-btn flat color="primary" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Outcome Variables
      </v-btn>
    </template>
    <v-card max-height="500px" class="rounded-lg">
      <v-card-title class="title primary--text text--darken-3">
        Outcome Variables
      </v-card-title>
      <v-sheet class="pa-3 background">
        <v-text-field
          v-model="searchVariable"
          label="Search Variable"
          dark
          flat
          solo-inverted
          hide-details
          clearable
          clear-icon="mdi-close-circle-outline"
        ></v-text-field>
      </v-sheet>
      <v-card-text>
        <v-treeview
          v-model="selectedObservationVariables"
          color="primary"
          :search="searchVariable"
          selectable
          return-object
          :items="observationVariables"
          item-text="label"
        ></v-treeview>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" flat @click="openInputVariableDialog = false"
          ><v-icon left dark>close</v-icon>Close</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';

export default {
  data: () => ({
    searchVariable: '',
    openInputVariableDialog: false,
    selectedObservationVariables: [],
    observationVariables: [],
  }),
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

<style lang="scss" scoped></style>
