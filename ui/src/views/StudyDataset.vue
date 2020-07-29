<template>
  <v-container fluid class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>library_books</v-icon>
      <v-toolbar-title class="white--text pl-2"
        >Saved Study Datasets
        <div class="subtitle-1">Select/View/Analyze Dataset</div>
      </v-toolbar-title>
    </v-app-bar>

    <v-container fluid fill-width class="pa-0 ma-0">
      <v-row class="pa-0 ma-0">
        <v-col cols="12" class="pa-0 ma-0">
          <v-sheet color="white" class="scroll rounded-lg shadow mt-2">
            <v-container fluid fill-width class="ma-0 pa-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <v-card color="#eeeeee" class="pt-1">
                    <v-card-title class="primary--text pl-3 py-2"
                      >Saved Study Datasets
                    </v-card-title>
                  </v-card>
                </v-col>
              </v-row>
            </v-container>

            <collection-table
              class="pb-1"
              show-collections="all"
            ></collection-table>
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script>
import CollectionTable from '@/components/DatasetManager/CollectionTable.vue';

export default {
  components: {
    CollectionTable,
  },
  computed: {},
  methods: {},
};
</script>

<style scoped></style>
