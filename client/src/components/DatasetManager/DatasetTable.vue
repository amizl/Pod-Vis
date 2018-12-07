<template lang='pug'>
v-card.elevation-3
  v-toolbar(
    card
    color="grey lighten-3"
    dense
  )
    v-icon table_chart
    v-toolbar-title Available Datasets
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
        hide-actions
        item-key='dataset'
      )
        template(
          slot="items"
          slot-scope="props"
        )
          tr
            td(@click.stop)
              v-checkbox(
                v-model='props.selected'
                primary
                hide-details
              )
            td {{ props.item.dataset }}
            td {{ props.item.n_samples }}
            td {{ props.item.outcome_categories }}
            td {{ props.item.outcome_measures }}
            td {{ props.item.demographics.length }}
            td {{ props.item.variables.length }}
            td
              v-tooltip(
                left
                color='primary'
              )
                v-icon(
                  @click='stepIntoDataset(props.item.id)'
                  slot="activator"
                ) info
                span More Info
            //- td {{ probs.item.n_variables }}
            //- td {{ props.item.code }}
</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import { state, actions } from '@/store/modules/datasetManager/types';

const { mapState, mapActions } = createNamespacedHelpers('datasetManager');

export default {
  components: {
    LoadingSpinner,
  },
  props: ['search'],
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
          text: 'Dataset',
          value: 'dataset',
        },
        {
          text: 'Subject Count',
          value: 'subject count',
        },
        {
          text: 'Outcome Categories',
          value: 'categories',
        },
        {
          text: 'Outcome Measures',
          value: 'measure',
        },
        {
          text: 'Demographics',
          value: 'demographics',
        },
        {
          text: 'Variables',
          value: 'variables',
        },
        {
          // text: 'More Info',
          value: 'moreInfo',
          sortable: false,
        }
      ],
      subheaders: [
        {
          text: 'Variable',
          value: 'variable',
        },
        {
          text: 'Type',
          value: 'type',
        },
        {
          text: 'Description',
          value: 'description',
        },
      ],
    };
  },
  computed: {
    ...mapState({
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
  methods: {
    ...mapActions({
      fetchDatasets: actions.FETCH_DATASETS,
      selectDatasets: actions.SELECT_DATASETS,
    }),
    stepIntoDataset(datasetId) {
      // Route to view for dataset information
      // const currentPath = this.$router.currentPath.fullPath;
      this.$router.push('datasetManager/dataset/' + datasetId)
    },
  },
  created() {
    if (!this.datasets) {
      this.fetchDatasets();
    }
  },
};
</script>

<style>
</style>
