<template>
  <div>
    <v-tooltip top color="primary">
    <template v-slot:activator="{ on }">
      <v-btn flat color="primary"  @click="openInputVariableDialog = !openInputVariableDialog" style="height:100%" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Outcome Variables
      </v-btn>
    </template>
    <span>Add/remove outcome variables from Summary View.</span>
    </v-tooltip>

  <v-dialog v-model="openInputVariableDialog" scrollable max-width="600px">
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
 </div>
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
    propagateChanges: false,
  }),
  computed: {
    ...mapState('dataExplorer', {
      collection: state.COLLECTION,
      outcomeVariables: state.OUTCOME_VARIABLES,
    }),
  },
  watch: {
    selectedObservationVariables(newObservationVariables) {
      // SCOPA, UPDRS, etc
      const outcomeMeasures = newObservationVariables.filter(
        variable => variable.parent_id != 1
      );
      // only propagate changes from dialog back to UI when dialog is open
      if (this.propagateChanges) {
        this.setOutcomeVariables(outcomeMeasures);
      }
    },
    openInputVariableDialog(open) {
      // ensure that dialog state matches UI state
      if (open) {
        this.updateSelectedObservationVariables();
      }
      // set flag to allow propagation of dialog changes back to UI
      this.propagateChanges = open;
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
    // ensure that dialog is in sync with outcome variables
    updateSelectedObservationVariables() {
      var new_selected_obs_vars = [];
      this.outcomeVariables.forEach(function(ov) {
        new_selected_obs_vars.push(ov);
      });
      this.selectedObservationVariables = new_selected_obs_vars;
    },
  },
};
</script>

<style lang="scss" scoped></style>
