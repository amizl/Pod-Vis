<template>
  <v-container fluid class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Dataset Manager - Use Saved Study Dataset
        <div class="subheading">Select Dataset</div>
      </v-toolbar-title>
    </v-toolbar>

    <v-sheet color="white" class="scroll rounded-lg shadow mt-2">
      <v-layout fill-height>
        <v-divider></v-divider>

        <v-flex xs12 class="pa-0 ma-0">
          <collection-table
            class="pb-1"
            show-collections="all"
          ></collection-table>
        </v-flex>
      </v-layout>
    </v-sheet>
  </v-container>
</template>

<script>
import CollectionTable from '@/components/dashboard/CollectionTable.vue';

export default {
  components: {
    CollectionTable,
  },
  computed: {},
  methods: {},
};
</script>

<style scoped></style>
