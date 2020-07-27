<template>
  <v-container fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>library_add</v-icon>
      <v-toolbar-title class="white--text pl-3"
        >Create New Study Dataset - Select Variables
        <div class="subtitle-1">Dataset: New Study Dataset (not saved)</div>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <v-chip
        :color="getNumSubjectsColor(numSubjects)"
        :text-color="getNumSubjectsTextColor(numSubjects)"
        class="title ma-2"
        >TOTAL SAMPLE: {{ numSubjects }} subjects selected</v-chip
      >

      <save-collection-btn-dialog
        :variables="variables"
        :dataset-ids="selectedDatasetIDs"
        :num-subjects-selected="numSubjects"
        :num-observation-vars-selected="numObservationVars"
        :num-subject-vars-selected="numSubjectVars"
        @dialogOpen="dialogOpened"
        @collectionSaved="collectionSaved"
      />
    </v-app-bar>

    <analysis-tracker
      :step.sync="step"
      :substep.sync="substep"
    ></analysis-tracker>

    <v-container fluid fill-width class="ma-0 pa-0 pt-2">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-sheet color="white" height="100%" class="rounded-lg shadow">
            <v-card color="#eeeeee" class="pt-1">
              <v-card-title class="primary--text pl-3 py-2"
                >Shared Variables</v-card-title
              >
              <v-card-subtitle class="primary--text pl-3"
                >Select the variables to include in the new study
                dataset.</v-card-subtitle
              >
            </v-card>

            <shared-variable-table
              v-model="selected"
              :datasets="selectedDatasets"
              selectable
              @nSubjects="updateNumSubjects"
              @nObservationVars="updateNumObservationVars"
              @nSubjectVars="updateNumSubjectVars"
            />
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import AnalysisTracker from '@/components/common/AnalysisTracker.vue';
import SharedVariableTable from '@/components/DatasetManager/SharedVariableTable.vue';
//import UnsharedVariableTable from '@/components/DatasetManager/UnsharedVariableTable.vue';
import SaveCollectionBtnDialog from '@/components/BuildDataset/SaveCollectionBtnDialog.vue';
import {
  colors,
  getNumSubjectsColor,
  getNumSubjectsTextColor,
} from '@/utils/colors';

export default {
  components: {
    AnalysisTracker,
    SharedVariableTable,
    //    UnsharedVariableTable,
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
    step: '2',
    substep: '2.2',
    numSubjects: 0,
    numObservationVars: 0,
    numSubjectVars: 0,
    colors: colors,
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
    getNumSubjectsColor,
    getNumSubjectsTextColor,
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
    updateNumObservationVars(no) {
      this.numObservationVars = no;
    },
    updateNumSubjectVars(ns) {
      this.numSubjectVars = ns;
    },
  },
};
</script>

<style scoped></style>
