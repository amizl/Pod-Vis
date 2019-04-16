<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Create Dataset Collection</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-btn :disabled="!selected.length" flat
          >SAVE NEW DATASET COLLECTION</v-btn
        >
      </v-toolbar-items>
    </v-toolbar>
    <v-layout row justify-center>
      <v-flex xs12>
        <p class="subheading grey--text ligthen-2">Selected Datasets:</p>
        <v-container grid-list-lg fluid pt-0 mt-0 pl-0 ml-0>
          <v-layout row wrap>
            <v-flex v-for="dataset in selectedDatasets" :key="dataset.id" xs4>
              <v-card>
                <v-card-title primary-title>
                  <span class="subheading">
                    {{ dataset.study_name }} <br />
                    <span class="caption grey--text lighten-2">
                      {{ dataset.project_name }}
                    </span>
                  </span>
                </v-card-title>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn :to="`/datasets/${dataset.id}`" flat icon>
                    <v-tooltip top color="primary">
                      <v-icon slot="activator"> info </v-icon>
                      <span>Learn more about this study</span>
                    </v-tooltip>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-flex>
          </v-layout>
        </v-container>
      </v-flex>
    </v-layout>
    <v-layout class="pt-2" row justify-center>
      <v-flex xs12>
        <v-card>
          <v-card-title card color="white">
            <p>
              <span class="title"
                >Shared Outcome Measures in Selected Datasets</span
              >
              <br />
              <span class="subheading grey--text ligthen-2"
                >Select the variables to include in the new dataset
                collection.</span
              >
            </p>
          </v-card-title>
          <variable-table v-model="selected" :dataset-id="id" selectable />
        </v-card>
      </v-flex>
    </v-layout>
    <v-layout class="pt-4" row justify-center>
      <v-flex xs12>
        <v-card>
          <v-tabs v-model="activeDataset" slider-color="primary">
            <v-tab v-for="dataset in selectedDatasets" :key="dataset.id">
              {{ dataset.study_name }}
            </v-tab>
            <v-tab-item v-for="dataset in selectedDatasets" :key="dataset.id">
              <variable-table :dataset-id="dataset.id" />
            </v-tab-item>
          </v-tabs>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import VariableTable from '@/components/DatasetManager/VariableTable.vue';

export default {
  components: {
    VariableTable,
  },
  props: {
    // id is passed in via route parameters
    // i.e., /build?id=x&id=y
    id: {
      type: [String, Array],
      default: null,
    },
  },
  data() {
    return {
      activeDataset: null,
      selected: [],
    };
  },
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
  },
  methods: {
    ...mapActions('datasetManager', {
      addSelectedDatasetsToCohorts: actions.ADD_SELECTED_DATASETS_TO_COHORTS,
    }),
    goBack() {
      this.$router.go(-1);
    },
  },
};
</script>

<style scoped></style>
