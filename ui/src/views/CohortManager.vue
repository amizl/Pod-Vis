<template>
  <v-container fluid grid-list-xl>
    <v-toolbar app class="white">
      <v-toolbar-title>Cohort Manager</v-toolbar-title>
    </v-toolbar>
    <v-layout row wrap justify-center>
      <v-flex xs12>
        <v-card>
          <v-card-title card color="white"
            ><span class="title">Cohorts</span>
          </v-card-title>
          <cohort-table></cohort-table>
        </v-card>
      </v-flex>
    </v-layout>
    <v-layout row wrap justify-center>
      <v-flex xs12>
        <v-card>
          <v-card-title card color="white"
            ><span class="title">Collections</span>
          </v-card-title>
          <collection-table></collection-table>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import CohortTable from '@/components/CohortManager/CohortTable.vue';
import CollectionTable from '@/components/common/CollectionTable.vue';

export default {
  components: {
    CohortTable,
    CollectionTable,
  },
  created() {
    // Fetch cohorts here? (Currently being fetch in CohortTable component)
  },
};
</script>

<style scoped></style>
