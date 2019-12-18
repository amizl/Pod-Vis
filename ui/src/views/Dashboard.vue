<template>
  <v-container fluid class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Home Page</v-toolbar-title>
    </v-toolbar>

    <v-sheet color="white" height="100%" class="scroll rounded-lg shadow">
      <!--    <v-card-title class="title primary--text"><v-chip color="primary" class="title white--text">A</v-chip> Begin a new analysis:</v-card-title> -->
      <v-card-title class="title primary--text"
        >Begin a new analysis:</v-card-title
      >
      <v-divider></v-divider>
      <analysis-tracker step="1" substep="1.0"></analysis-tracker>
    </v-sheet>

    <v-sheet color="white" height="100%" class="scroll rounded-lg shadow mt-2">
      <!--    <v-card-title class="title primary--text"><v-chip color="primary" class="title white--text">B</v-chip> Continue or revisit a saved analysis:</v-card-title> -->
      <v-card-title class="title primary--text"
        >Continue or revisit a saved analysis:</v-card-title
      >
      <v-layout fill-height>
        <v-divider></v-divider>

        <!-- <v-layout align-center justify-center> -->
        <v-flex xs12 class="pa-0 ma-0">
          <v-tabs slider-color="primary" grow>
            <v-tab> <span class="">My Study Datasets</span> </v-tab>
            <v-tab-item>
              <collection-table
                class="pb-1"
                :show-public-collections="false"
              ></collection-table>
            </v-tab-item>

            <v-tab> <span class="">Public Study Datasets</span> </v-tab>
            <v-tab-item>
              <collection-table
                class="pb-1"
                :show-public-collections="true"
              ></collection-table>
            </v-tab-item>
          </v-tabs>
        </v-flex>
      </v-layout>
    </v-sheet>
  </v-container>
</template>

<script>
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import CollectionTable from '@/components/dashboard/CollectionTable.vue';

export default {
  components: {
    CollectionTable,
    AnalysisTracker,
  },
  computed: {},
  created() {},
  methods: {},
};
</script>

<style scoped></style>
