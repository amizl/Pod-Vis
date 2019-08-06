<template>
  <v-container v-if="isLoading" fluid fill-height>
    <loading-spinner />
  </v-container>
  <v-container v-else fluid fill-height grid-list-md>
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Data Explorer</v-toolbar-title>
    </v-toolbar>
    <v-layout column fill-height>
      <v-flex>
        <v-layout fill-height>
          <v-flex xs3>
            <v-sheet color="white" height="100%" class="rounded-lg shadow">
              <v-card-title class="title primary--text">
                Outcome Variables
              </v-card-title>
              <v-divider></v-divider>
            </v-sheet>
          </v-flex>
          <v-flex xs9>
            <v-sheet color="white" height="100%" class="rounded-lg shadow">
              <v-card-title class="title primary--text"
                >Summary View</v-card-title
              >
              <v-divider></v-divider>
            </v-sheet>
          </v-flex>
        </v-layout>
      </v-flex>
      <v-flex>
        <v-layout fill-height>
          <v-flex xs3>
            <v-sheet color="white" height="100%" class="rounded-lg shadow">
              <v-card-title class="title primary--text">Cohorts</v-card-title>
              <v-divider></v-divider>
            </v-sheet>
          </v-flex>
          <v-flex>
            <v-sheet color="white" height="100%" class="rounded-lg shadow">
              <v-card-title class="title primary--text"
                >Detailed View</v-card-title
              >
              <v-divider></v-divider>
            </v-sheet>
          </v-flex>
        </v-layout>
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
    SummaryViewCard,
    DetailedViewCard,
    DatasetSummaryCard,
  },
  data() {
    return {
      isLoading: false,
    };
  },
  created() {},
};
</script>

<style scoped></style>
