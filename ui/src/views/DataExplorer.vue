<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Data Explorer</v-toolbar-title>
    </v-toolbar>
    <v-layout row wrap>
      <v-flex xs12>
        <v-card color="blue-grey darken-2" class="white--text">
          DatasetSummaryCard here
          <!-- Import DataExplorer/DatasetSummaryCard.vue -->
        </v-card>
      </v-flex>
      <v-flex xs12>
        <v-card color="green darken-2" class="white--text">
          <SummaryViewCard></SummaryViewCard>
          <!-- Import DataExplorer/SummaryViewCard.vue -->
        </v-card>
      </v-flex>
      <v-flex xs12>
        <v-card color="blue darken-2" class="white--text">
          DetailedViewCard here
          <!-- Import DataExplorer/DetailedViewCard.vue -->
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import DatasetSummaryCard from '@/components/DataExplorer/DatasetSummaryCard.vue';
import DetailedViewCard from '@/components/DataExplorer/DetailedViewCard.vue';
import SummaryViewCard from '@/components/DataExplorer/SummaryViewCard.vue';

export default {
    components: {
        SummaryViewCard, DetailedViewCard, DatasetSummaryCard
    }
};
</script>

<style scoped></style>
