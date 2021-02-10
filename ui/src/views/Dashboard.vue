<template>
  <v-container fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>home</v-icon>
      <v-toolbar-title class="white--text pl-2">Home Page</v-toolbar-title>
    </v-app-bar>

    <v-sheet color="white" class="scroll rounded-lg shadow my-2">
      <v-container fluid fill-width class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-card color="#eeeeee" class="pt-1">
              <v-card-title class="primary--text pl-3 py-2"
                >Welcome to POD-Vis
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <v-container class="ma-2 my-4">
        <v-row>
          <v-col cols="12">
            <div class="text--primary title">
              Please choose one of the following options to get started:
            </div>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-btn color="primary" @click="$router.push('/datasets')"
              ><v-icon left large color="white">library_add</v-icon
              ><span class="pl-2">Create new study dataset</span></v-btn
            >
            <span class="pl-2"
              >- select subjects and variables from uploaded dataset(s) to
              create a new study dataset.</span
            >
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-btn color="primary" @click="$router.push('/study_datasets')"
              ><v-icon left large color="white">library_books</v-icon
              ><span class="pl-2">Use saved study dataset</span></v-btn
            >
            <span class="pl-2"
              >- use a previously-created saved study dataset to continue or
              revisit an analysis.</span
            >
          </v-col>
        </v-row>

        <v-row> <v-col cols="12"> </v-col> </v-row>
      </v-container>
    </v-sheet>
  </v-container>
</template>

<script>
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';

export default {
  components: {
    AnalysisTracker,
  },
  data() {
    return {
      selected_action: null,
    };
  },
  computed: {},
  methods: {},
};
</script>

<style scoped></style>
