<template>
  <v-container fluid grid-list-md class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Create Clinical Data Collection</v-toolbar-title
      >
      <v-spacer></v-spacer>
      <save-collection-btn-dialog
        :variables="variables"
        :dataset-ids="selectedDatasetIDs"
      />
    </v-toolbar>
    <!-- <v-layout row justify-center>
      <v-flex xs12>
        <p class="subheading grey--text ligthen-2">Selected Datasets:</p>
        <v-container grid-list-lg fluid pt-0 mt-0 pl-0 ml-0>
          <v-layout row wrap>
            <v-flex v-for="dataset in selectedDatasets" :key="dataset.id" xs4>
              <sunburst-card
                :id="dataset.id"
                :project-name="dataset.project_name"
                :study-name="dataset.study_name"
              />
            </v-flex>
          </v-layout>
        </v-container>
      </v-flex>
    </v-layout> -->

    <v-layout column>
      <v-flex>
        <v-layout>
          <v-flex xs12>
            <v-card flat class="shadow rounded-lg">
              <v-card-title card color="white">
                <p>
                  <span class="title primary--text">Shared Variables</span>
                  <br />
                  <span class="subheading grey--text ligthen-2"
                    >Select the variables to include in the new clinical data
                    collection.</span
                  >
                </p>
              </v-card-title>
              <shared-variable-table
                v-model="selected"
                :datasets="selectedDatasets"
                selectable
              />
            </v-card>
          </v-flex>
        </v-layout>
      </v-flex>
      <v-flex>
        <v-layout row justify-center>
          <v-flex xs12>
            <v-card flat class="shadow rounded-lg">
              <v-card-title card color="white">
                <p>
                  <span class="title primary--text">Unshared Variables</span>
                  <br />
                  <span class="subheading grey--text ligthen-2"
                    >These variables are not shared among the selected datasets.
                  </span>
                </p>
              </v-card-title>
              <v-tabs v-model="activeDataset" slider-color="primary">
                <v-tab v-for="dataset in selectedDatasets" :key="dataset.id">
                  {{ dataset.study_name }}
                </v-tab>
                <v-tab-item
                  v-for="dataset in selectedDatasets"
                  :key="dataset.id"
                >
                  <unshared-variable-table
                    :selected-ids="selectedDatasets.map(d => d.id)"
                    :dataset-id="dataset.id"
                  />
                </v-tab-item>
              </v-tabs>
            </v-card>
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import SharedVariableTable from '@/components/DatasetManager/SharedVariableTable.vue';
import UnsharedVariableTable from '@/components/DatasetManager/UnsharedVariableTable.vue';
import SaveCollectionBtnDialog from '@/components/BuildDataset/SaveCollectionBtnDialog.vue';

export default {
  components: {
    SharedVariableTable,
    UnsharedVariableTable,
    SaveCollectionBtnDialog,
  },
  props: {
    // id is passed in via route parameters
    // i.e., /build?id=x&id=y
    id: {
      type: [String, Array],
      default: null,
    },
  },
  data: () => ({
    collectionName: '',
    activeDataset: null,
    selected: [],
  }),
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
    selectedDatasetIDs() {
      return this.selectedDatasets.map(({ id }) => id);
    },
    variables() {
      return this.selected;
    },
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
