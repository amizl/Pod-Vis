<template>
  <section>
    <v-toolbar card dense flat color="white rounded-lg">
      <v-toolbar-items> <output-variables-dialog /> </v-toolbar-items>
      <v-divider vertical class="ml-4"></v-divider>
      <v-toolbar-items class="pl-4 pt-1 scrollable">
        <!-- TODO...filters? -->
      </v-toolbar-items>
    </v-toolbar>
    <v-divider></v-divider>
  </section>
</template>

<script>
import OutputVariablesDialog from '@/components/CohortManager/OutputVariablesDialog.vue';

export default {
  components: {
    OutputVariablesDialog,
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
.scrollable {
  overflow-x: auto;
}
.scrollable::-webkit-scrollbar {
  display: none;
}
</style>
