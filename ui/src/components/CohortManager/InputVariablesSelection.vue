<template>
  <v-card min-height="100%">
    <v-toolbar dense flat color="white">
      <v-toolbar-items>
        <v-dialog
          v-model="openInputVariableDialog"
          scrollable
          max-width="600px"
        >
          <template v-slot:activator="{ on }">
            <v-btn flat v-on="on">
              <v-icon left dark>add_box</v-icon> Input Variables
            </v-btn>
          </template>
          <v-card max-height="500px">
            <v-card-title class="title">Input Variables</v-card-title>
            <v-sheet class="pa-3 primary lighten-2">
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
              <input-variables-tree :search="searchVariable" />
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                flat
                @click="openInputVariableDialog = false"
                ><v-icon left dark>close</v-icon>Close</v-btn
              >
              <!-- <v-btn
                color="primary darken-1"
                flat
                @click="openInputVariableDialog = false"
                ><v-icon left dark>add_box</v-icon>ADD VARIABLES</v-btn
              > -->
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-toolbar-items>
      <v-divider vertical class="pl-4"></v-divider>
      <v-toolbar-items class="pl-4 pt-1">
        <v-chip
          v-for="variable in variables"
          :key="variable.label"
          class="handle"
          outline
          :color="variable.type == 'subject' ? 'blue' : 'green'"
        >
          {{ variable.label }}
        </v-chip>
      </v-toolbar-items>
    </v-toolbar>
    <v-divider />
  </v-card>
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
  computed: {
    filter() {
      return this.caseSensitive
        ? (item, search, textKey) => item[textKey].indexOf(search) > -1
        : undefined;
    },
  },
};
</script>

<style lang="scss" scoped></style>
