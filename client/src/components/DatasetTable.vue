<template lang='pug'>
v-card(
  v-if='loading'
  align-center
  justify-center
  height=500
  width=500
)
  half-circle-spinner(
    :animation-duration="1000"
    :size="60"
    :color="'#ff1d5e'"
  )
v-card(v-else).elevation-4
  v-data-table(
    v-model='selected'
    :search='search'
    :headers='headers'
    :items='datasets'
    hide-actions
    item-key='dataset'
  )
    template(slot="expand" slot-scope="props")
      v-card(flat)
        v-card-title(primary-title).ma-3
          h1 {{ props.item.dataset }}
        v-card-text.ma-3
          p {{ props.item.description}}
        v-data-table(
          :headers='subheaders'
          :items='props.item.variables'
        )
          template(slot="items" slot-scope="props")
            tr
              td {{ props.item.name }}
              td {{ props.item.type }}
              td {{ props.item.description }}
    template(slot="items" slot-scope="props")
      tr(@click="props.expanded = !props.expanded")
        td {{ props.item.dataset }}
        td {{ props.item.code }}
        td(@click.stop)
          v-checkbox(
            v-model='props.selected'
            primary
            hide-details
          )
</template>

<script>
import { HalfCircleSpinner } from 'epic-spinners';
import { createNamespacedHelpers } from 'vuex';
import { getters, actions } from '@/store/modules/datasetManager/types';

const { mapGetters, mapActions } = createNamespacedHelpers('datasetManager');

/*eslint-disable*/
export default {
  components: {
    HalfCircleSpinner
  },
  props: ['search'],
  data () {
    return {
      selected: [],
      headers: [
        {
          text: 'Dataset',
          value: 'dataset',
        },
        {
          text: 'Code',
          value: 'code',
        },
        {
          text: 'Selected',
          value: 'selected',
          sortable: false,
        },
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
    ...mapGetters({
      loading: getters.LOADING,
      datasets: getters.DATASETS,
      selected_datasets: getters.SELECTED_DATASETS,
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
    })
  },
  created() {
    if (!this.datasets) {
        this.fetchDatasets();
    }
  },
}
</script>

<style>
</style>



