<template>
  <loading-spinner v-if="!datasets" medium class="pb-5"></loading-spinner>
  <v-data-table
    v-else
    v-model="selected"
    :search="search"
    :headers="headers"
    :items="datasets"
    item-key="study_name"
    class="pb-1"
    hide-actions
  >
    <template v-slot:items="props">
      <tr>
        <td>
          <v-checkbox
            v-model="props.selected"
            color="primary"
            hide-details
          ></v-checkbox>
        </td>
        <td class="text-xs-left">{{ props.item.project_name }}</td>
        <td class="text-xs-left">{{ props.item.study_name }}</td>
        <td class="text-xs-left">{{ props.item.num_subjects }}</td>
        <td class="text-xs-left">
          {{ props.item.longitudinal ? 'Yes' : 'No' }}
        </td>
        <!-- <td class="text-xs-right">{{ props.item.n_samples }}</td>
        <td class="text-xs-right">{{ props.item.outcome_categories }}</td>
        <td class="text-xs-right">{{ props.item.outcome_measures }}</td>
        <td class="text-xs-right">{{ props.item.demographics.length }}</td>
        <td class="text-xs-right">{{ props.item.variables.length }}</td> -->
        <td class="text-xs-right justify-center">
          <v-tooltip top color="primary">
            <template v-slot:activator="{ on }">
              <v-icon
                color="primary"
                class="mr-1"
                @click="stepIntoDataset(props.item.id)"
                v-on="on"
                >info</v-icon
              >
            </template>
            <span
              >Learn more about
              <strong>{{ props.item.study_name }}</strong></span
            >
          </v-tooltip>
        </td>
      </tr>
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
          text: 'Selected',
          value: 'selected',
          sortable: false,
        },
        {
          text: 'Project',
          value: 'project_name',
        },
        {
          text: 'Study',
          value: 'study_name',
        },
        {
          text: 'Subject Count',
          value: 'num_subjects',
        },
        {
          text: 'Longitudinal?',
          value: 'longitudinal',
        },
        // {
        //   text: 'Outcome Categories',
        //   value: 'categories',
        // },
        // {
        //   text: 'Outcome Measures',
        //   value: 'measure',
        // },
        // {
        //   text: 'Demographics',
        //   value: 'demographics',
        // },
        // {
        //   text: 'Variables',
        //   value: 'variables',
        // },
        {
          text: '',
          value: 'name',
          sortable: false,
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
