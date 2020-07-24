<template>
  <loading-spinner v-if="!datasets" medium class="pb-5"></loading-spinner>
  <v-data-table
    v-else
    v-model="selected"
    show-select
    :search="search"
    :headers="headers"
    :items="datasets"
    item-key="study_name"
    class="pb-1"
    hide-default-footer
  >
    <template v-slot:item.project_name="{ item }">
      <td class="subtitle-1 text-xs-left">{{ item.project_name }}</td>
    </template>

    <template v-slot:item.study_name="{ item }">
      <td class="subtitle-1 text-xs-left">{{ item.study_name }}</td>
    </template>

    <template v-slot:item.num_subjects="{ item }">
      <td class="subtitle-1 text-xs-left">{{ item.num_subjects }}</td>
    </template>

    <template v-slot:item.longitudinal="{ item }">
      <td class="subtitle-1 text-xs-left">
        {{ item.longitudinal ? 'Yes' : 'No' }}
      </td>
    </template>

    <template v-slot:item.name="{ item }">
      <td class="text-subtitle-1 text-xs-left">
        <v-tooltip top color="primary">
          <template v-slot:activator="{ on }">
            <v-icon
              color="primary"
              class="mr-1"
              @click="stepIntoDataset(item.id)"
              v-on="on"
              >info</v-icon
            >
          </template>
          <span>Learn more about this dataset.</span>
        </v-tooltip>
      </td>
    </template>
  </v-data-table>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';

export default {
  props: {
    search: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      selected: [],
      headers: [
        {
          text: 'Project',
          value: 'project_name',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Dataset',
          value: 'study_name',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Subject Count',
          value: 'num_subjects',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Longitudinal?',
          value: 'longitudinal',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Info',
          value: 'name',
          align: 'left',
          sortable: false,
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
    };
  },
  computed: {
    ...mapState('datasetManager', {
      isLoading: state.IS_LOADING,
      datasets: state.DATASETS,
      selectedDatasets: state.SELECTED_DATASETS,
    }),
    // TODO: Look at making this work.
    // selected ends up being specific selected element
    // rather than current list of selected elements.
    // Using watch in the mean time to update store state.
    // selected: {
    //   set(selected) {
    //     console.log(selected);
    //     this.selectDatasets(selected);
    //   },
    //   get() {
    //     this.selected_datasets;
    //   },
    // },
  },
  watch: {
    selected() {
      this.selectDatasets(this.selected);
    },
  },
  created() {
    if (!this.datasets) {
      this.fetchDatasets();
    } else {
      this.selected = this.selectedDatasets;
    }
  },
  methods: {
    ...mapActions('datasetManager', {
      fetchDatasets: actions.FETCH_DATASETS,
      selectDatasets: actions.SELECT_DATASETS,
    }),
    stepIntoDataset(studyID) {
      // Route to view for dataset information
      // const currentPath = this.$router.currentPath.fullPath;
      this.$router.push(`datasets/${studyID}`);
    },
  },
};
</script>

<style></style>
