<template>
  <section>
    <v-toolbar card dense flat color="white rounded-lg">
      <v-toolbar-items> <input-variables-dialog /> </v-toolbar-items>
      <v-divider vertical class="ml-4"></v-divider>
      <v-toolbar-items class="pl-4 pt-1 scrollable">
        <input-variables-selected-chips />
      </v-toolbar-items>
    </v-toolbar>
    <v-divider></v-divider>
  </section>
</template>

<script>
import InputVariablesDialog from '@/components/CohortManager/InputVariablesDialog.vue';
import InputVariablesSelectedChips from '@/components/CohortManager/InputVariablesSelectedChips.vue';

export default {
  components: {
    InputVariablesDialog,
    InputVariablesSelectedChips,
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
