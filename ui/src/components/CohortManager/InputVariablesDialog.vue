<template>
  <v-dialog v-model="openInputVariableDialog" scrollable max-width="600px">
    <template v-slot:activator="{ on }">
      <v-btn flat color="primary" class="title" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Choose Predictor Variables
      </v-btn>
    </template>
    <v-card max-height="500px" class="rounded-lg">
      <v-card-title class="title primary--text text--darken-3">
        Choose Predictor Variables
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
        <input-variables-tree ref="inputVars" :search="searchVariable" />
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
import InputVariablesTree from '@/components/CohortManager/InputVariablesTree.vue';

export default {
  components: {
    InputVariablesTree,
  },
  data: () => ({
    searchVariable: '',
    openInputVariableDialog: false,
  }),
  watch: {
    openInputVariableDialog(open) {
      // set flag to allow propagation of dialog changes back to UI
      this.$refs.inputVars.propagateChanges = open;
      if (open) {
        this.$emit('dialogOpened', true);
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
