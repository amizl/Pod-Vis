<template>
  <section>
    <v-toolbar card dense flat color="white rounded-lg">
      <!-- <v-toolbar-items> <input-variables-dialog /> </v-toolbar-items> -->
      <span class="title primary--text">Summary View</span>
      <v-divider vertical class="ml-4"></v-divider>
      <v-toolbar-items> <outcome-variables-dialog /> </v-toolbar-items>
      <v-spacer />
      <!-- <v-toolbar-items>
      </v-toolbar-items> -->
      <!-- <v-spacer></v-spacer>
      <v-select
        :items="['Cohort']"
        menu-props="auto"
        label="Select"
        hide-details
        append-icon="format_color_fill"
        color="primary"
      ></v-select> -->
      <!-- <v-spacer></v-spacer> -->
    </v-toolbar>
    <v-divider></v-divider>
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
