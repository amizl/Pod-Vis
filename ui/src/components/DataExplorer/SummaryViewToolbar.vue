<template>
  <section>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">

    <v-toolbar card dense flat color="white rounded-lg">
      <span class="title primary--text">Summary View</span>
      <v-divider vertical class="ml-4"></v-divider>
      <v-toolbar-items> <outcome-variables-dialog /> </v-toolbar-items>

    </v-toolbar>
    <v-divider></v-divider>
    </v-layout>
  </v-sheet>

  </section>
</template>

<script>
import OutcomeVariablesDialog from '@/components/DataExplorer/OutcomeVariablesDialog.vue';

export default {
  components: {
    OutcomeVariablesDialog,
  },
};
</script>

<style lang="scss" scoped></style>
