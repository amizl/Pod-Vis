<template>
  <v-dialog v-model="openOutputVariableDialog" scrollable>
    <template v-slot:activator="{ on }">
      <v-btn flat color="primary" class="title" v-on="on">
        <v-icon left dark>add_box</v-icon>
        Choose Outcome Variables
      </v-btn>
    </template>
    <v-card max-height="500px">
      <v-card-title class="title primary--text text--darken-3">
        Choose Outcome Variables
      </v-card-title>
      <v-card-text>
        <output-variables-table ref="outputVars" :search="searchVariable" />
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
import OutputVariablesTable from '@/components/CohortManager/OutputVariablesTable.vue';

export default {
  components: {
    OutputVariablesTable,
  },
  data: () => ({
    searchVariable: '',
    openOutputVariableDialog: false,
  }),
  watch: {
    openOutputVariableDialog(open) {
      // set flag to allow propagation of dialog changes back to UI
      this.$refs.outputVars.propagateChanges = open;
      if (open) {
        this.$emit('dialogOpened', true);
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
