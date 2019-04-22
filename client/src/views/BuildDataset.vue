<template>
  <v-container fluid>
    <v-toolbar app class="white">
      <v-toolbar-title>Create Dataset</v-toolbar-title>
      <v-spacer></v-spacer>
      <save-collection-btn-dialog
        :variables="variables"
        :dataset-ids="selectedDatasetIDs"
      />
    </v-toolbar>
    <v-layout row justify-center>
      <v-flex xs12>
        <p class="subheading grey--text ligthen-2">Selected Datasets:</p>
        <v-container grid-list-lg fluid pt-0 mt-0 pl-0 ml-0>
          <v-layout row wrap>
            <!-- TODO: Possibly strip this card into their own component -->
            <v-flex v-for="dataset in selectedDatasets" :key="dataset.id" xs4>
              <sunburst-card
                :id="dataset.id"
                :project-name="dataset.project_name"
                :study-name="dataset.study_name"
              />
            </v-flex>
            <!-- ^^^^ -->
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
import SaveCollectionBtnDialog from '@/components/BuildDataset/SaveCollectionBtnDialog.vue';
import SunburstCard from '@/components/BuildDataset/SunburstCard.vue';

export default {
  components: {
    VariableTable,
    SaveCollectionBtnDialog,
    SunburstCard,
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
      // Variable take on the shape of {category, scale}. We
      // only really need the scale (for now).
      return this.selected.map(variable => variable.scale);
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
