<template>
  <div>
    <v-app-bar dense text class="rounded-lg">
      <v-toolbar-title class="primary--text title">
        Summary View
      </v-toolbar-title>

      <v-divider vertical class="ml-4 mr-4"> </v-divider>

      <v-spacer />

      <v-toolbar-items> <outcome-variables-dialog /> </v-toolbar-items>
    </v-app-bar>
  </div>
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
