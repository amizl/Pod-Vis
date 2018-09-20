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
  v-card-title
    v-spacer
      v-text-field(
        v-model="search"
        append-icon="search"
        label="Search for Dataset"
        single-line
        hide-details
      ).ma-1
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

/*eslint-disable*/
export default {
  components: {
    HalfCircleSpinner
  },
  data () {
    return {
      search: '',
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
    loading() {
      return this.$store.getters.loading;
    },
    datasets() {
      return this.$store.getters.browserDatasets;
    },
  },
  watch: {
    selected() {
      this.$emit('dataSelected', this.selected);
    },
  },
  methods: {
  },
  created() {
    if (!this.datasets) {
        this
          .$store
          .dispatch('fetchBrowserDatasets');
      }
  },
}
</script>

<style>
</style>



