<template>
  <v-container fluid grid-list-md class="ma-0 pa-2">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text"
        >Dataset Manager - Select Variables</v-toolbar-title
      >
      <v-spacer></v-spacer>
      <v-toolbar-items>
        <v-chip
          disabled
          :color="getNumSubjectsColor(numSubjects)"
          class="primary--text title ma-2"
          >{{ numSubjects }} subjects selected</v-chip
        >
      </v-toolbar-items>

      <save-collection-btn-dialog
        :variables="variables"
        :dataset-ids="selectedDatasetIDs"
        :num-subjects-selected="numSubjects"
        @dialogOpen="dialogOpened"
        @collectionSaved="collectionSaved"
      />
    </v-toolbar>

    <v-sheet color="white" height="100%" class="scroll rounded-lg shadow">
      <analysis-tracker step="2" :substep="substep"></analysis-tracker>
    </v-sheet>

    <!-- <v-layout row justify-center>
      <v-flex xs12>
        <p class="subheading grey--text lighten-2">Selected Datasets:</p>
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
                  <span class="subtitle-1 grey--text lighten-2"
                    >Select the variables to include in the new study
                    dataset.</span
                  >
                </p>
              </v-card-title>
              <shared-variable-table
                v-model="selected"
                :datasets="selectedDatasets"
                selectable
                @nSubjects="updateNumSubjects"
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
                  <span class="subtitle-1 grey--text ligthen-2"
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
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import SharedVariableTable from '@/components/DatasetManager/SharedVariableTable.vue';
import UnsharedVariableTable from '@/components/DatasetManager/UnsharedVariableTable.vue';
import SaveCollectionBtnDialog from '@/components/BuildDataset/SaveCollectionBtnDialog.vue';

export default {
  components: {
    AnalysisTracker,
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
    substep: '2.2',
    numSubjects: 0,
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
    dialogOpened(isOpen) {
      if (isOpen) {
        this.substep = '2.3';
      } else {
        this.substep = '2.2';
      }
    },
    collectionSaved() {
      this.step = '3';
    },
    updateNumSubjects(ns) {
      this.numSubjects = ns;
    },
    // TODO - duplicated from SharedVariableTable.vue
    getNumSubjectsColor(nSubjects) {
      if (nSubjects <= 10) {
        return '#F83008';
      } else if (nSubjects <= 25) {
        return '#F8B108';
      } else {
        return '#FAE1A6';
      }
    },
  },
};
</script>

<style scoped></style>
