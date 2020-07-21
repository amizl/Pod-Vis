<template>
  <v-container fluid class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>home</v-icon>
      <v-toolbar-title class="white--text pl-2">Home Page</v-toolbar-title>
    </v-app-bar>

    <analysis-tracker
      :step.sync="step"
      :substep.sync="substep"
    ></analysis-tracker>

    <v-sheet color="white" class="scroll rounded-lg shadow mt-2">
      <v-container class="ma-2">
        <v-row>
          <v-col cols="12">
            <div class="title">Welcome to POD-Vis</div>
            <div class="text--primary subtitle mt-4">
              Please choose one of the following options to get started:
            </div>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="3">
            <v-btn color="primary" @click="$router.push('/datasets')"
              ><v-icon left large color="white">library_add</v-icon
              ><span class="pl-2">Create new study dataset</span></v-btn
            >
          </v-col>
          <v-col cols="9">
            Select subjects and variables from uploaded dataset(s) to create a
            new study dataset.
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="3">
            <v-btn color="primary" @click="$router.push('/study_datasets')"
              ><v-icon left large color="white">library_books</v-icon
              ><span class="pl-2">Use saved study dataset</span></v-btn
            >
          </v-col>
          <v-col cols="9">
            Use a previously-created saved study dataset to continue or revisit
            an analysis.
          </v-col>
        </v-row>
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
      step: '1',
      substep: '1.0',
    };
  },
  computed: {},
  methods: {},
};
</script>

<style scoped></style>
