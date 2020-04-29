<template>
  <v-dialog v-model="openInputVariableDialog" scrollable>
    <template v-slot:activator="{ on }">
      <v-btn flat color="primary" class="title" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Choose Predictor Variables
      </v-btn>
    </template>
    <v-card class="rounded-lg">
      <v-card-title class="title primary--text text--darken-3">
        Choose Predictor Variables
      </v-card-title>
      <v-card-text>
        <input-variables-table ref="inputVars" :search="searchVariable" />
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
import InputVariablesTable from '@/components/CohortManager/InputVariablesTable.vue';

export default {
  components: {
    InputVariablesTable,
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
