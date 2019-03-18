<template lang="pug">
v-card
  //- v-toolbar(
  //-   card
  //-   color="grey lighten-3"
  //-   dense
  //- )
  //-   v-icon table_chart
  //-   v-toolbar-title Available Datasets
  v-layout(
    row
    justify-center
    align-center
  )
    v-flex(v-if='isLoading')
      loading-spinner(medium).ma-5
    v-flex(v-else)
      v-data-table(
        v-if='datasets'
        v-model='selected'
        :search='search'
        :headers='headers'
        :items='datasets'
        item-key='study_name'
        hide-actions
      )
        template(
          slot="items"
          slot-scope="props"
        )
          tr
            td
              v-checkbox(
                v-model='props.selected'
                color='primary'
                hide-details
              )
            td.text-xs-left {{ props.item.project_name }}
            td.text-xs-left {{ props.item.study_name }}
            //- td.text-xs-right {{ props.item.n_samples }}
            //- td.text-xs-right {{ props.item.outcome_categories }}
            //- td.text-xs-right {{ props.item.outcome_measures }}
            //- td.text-xs-right {{ props.item.demographics.length }}
            //- td.text-xs-right {{ props.item.variables.length }}
            //- td.text-xs-right.justify-center.layout.mt-4
            td.text-xs-right.justify-center
              v-tooltip(
                top
                color='primary'
              )
                v-icon(
                  @click='stepIntoDataset(props.item.id)'
                  slot="activator"
                  color='primary'
                ).mr-1 info
                span Learn more about this study
              //- v-tooltip(
              //-   top
              //-   color='primary'
              //- )
              //-   //- @click='addToProfile({ dataset: props.item.dataset, id:props.item.id })'
              //-   v-icon(
              //-     @click='addToProfile(props.item.study_id)'
              //-     slot="activator"
              //-     color='primary'
              //-   ) add_circle
              //-   span Add dataset to profile
            //- td {{ probs.item.n_variables }}
            //- td {{ props.item.code }}
  v-snackbar(
      v-model='addToProfileSuccess'
      color='success'
      top
  )
    | Dataset was successfully added to your profile.
</template>

<script>
import { mapState, mapActions } from 'vuex';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import { state, actions } from '@/store/modules/datasetManager/types';
import { actions as dashboardActions } from '@/store/modules/dashboard/types';

export default {
  components: {
    LoadingSpinner,
  },
  props: {
    search: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      addToProfileSuccess: false,
      addToProfileFailure: false,
      selected: [],
      headers: [
        {
          text: 'Selected',
          value: 'selected',
          sortable: false,
        },
        {
          text: 'Project',
          value: 'project',
        },
        {
          text: 'Study',
          value: 'study',
        },
        // {
        //   text: 'Subject Count',
        //   value: 'subject count',
        // },
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
    ...mapActions('dashboard', {
      addToProfile: dashboardActions.ADD_DATASET_TO_PROFILE,
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
