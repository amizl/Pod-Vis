<template>
  <v-dialog v-model="openOutputVariableDialog" scrollable max-width="600px">
    <template v-slot:activator="{ on }">
      <v-btn flat color="primary" class="title" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Outcome Variables
      </v-btn>
    </template>
    <v-card max-height="500px">
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
        <output-variables-tree ref="outputVars" :search="searchVariable" />
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" flat @click="openOutputVariableDialog = false"
          ><v-icon left dark>close</v-icon>Close</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import OutputVariablesTree from '@/components/CohortManager/OutputVariablesTree.vue';

export default {
  components: {
    OutputVariablesTree,
  },
  data: () => ({
    searchVariable: '',
    openOutputVariableDialog: false,
  }),
  watch: {
    openOutputVariableDialog(open) {
      // set flag to allow propagation of dialog changes back to UI
      this.$refs.outputVars.propagateChanges = open;
    },
  },
};
</script>

<style lang="scss" scoped></style>
