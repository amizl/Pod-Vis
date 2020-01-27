<template>
  <v-container fluid class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Home Page</v-toolbar-title>
    </v-toolbar>

    <analysis-tracker step="1" substep="1.0"></analysis-tracker>

    <v-sheet color="white" class="scroll rounded-lg shadow mt-2">
      <v-flex xs12 class="pa-0 ma-0">
        <v-card>
          <v-card-text>
            <div class="subtitle-1">Welcome to POD-Vis</div>
            <!--
	    <div class="text--primary subtitle-2 mt-3">About POD-Vis</div>
	    <div class="subheading">POD-Vis is a </div>
-->
            <div class="text--primary subtitle-2 mt-4">
              Please choose one of the following options to get started:
            </div>
          </v-card-text>
          <v-card-actions>
            <v-container fluid fill-width>
              <v-layout row wrap>
                <v-flex xs3>
                  <div class="text-xs-center">
                    <v-btn color="primary" @click="$router.push('/datasets')"
                      >Create new study dataset</v-btn
                    >
                  </div>
                </v-flex>
                <v-flex xs9 class="pl-2">
                  Select subjects and variables from uploaded dataset(s) to
                  create a new study dataset.
                </v-flex>

                <v-flex xs12><div height="0.5em">&nbsp;</div></v-flex>

                <v-flex xs3>
                  <div class="text-xs-center">
                    <v-btn
                      color="primary"
                      @click="$router.push('/study_datasets')"
                      >Use saved study dataset</v-btn
                    >
                  </div>
                </v-flex>
                <v-flex xs9 class="pl-2">
                  Use a previously-created saved study dataset to continue or
                  revisit an analysis.
                </v-flex>
              </v-layout>
            </v-container>
          </v-card-actions>
        </v-card>
      </v-flex>
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
