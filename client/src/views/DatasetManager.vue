<template lang='pug'>
v-container(fluid fill-height grid-list-xl)
  v-toolbar(
    app
  ).primary
    v-layout
      v-flex(xs6)
        v-text-field(
          v-model="search"
          prepend-icon="search"
          label="Search for Dataset"
          single-line
          hide-details
          dark
        )
  v-layout(row wrap)
    v-flex(xs6)
      dataset-table(:search='search')
    v-flex(xs6 fill-height)
      donut-chart(v-if='selected_datasets', :data='selected_datasets')
</template>

<script>
import { createNamespacedHelpers } from 'vuex';
import { getters } from '@/store/modules/datasetManager/types';
import Header from '../components/layout/Header.vue';
import DatasetTable from '../components/DatasetTable.vue';
import DonutChart from '../components/charts/DonutChart.vue';

const { mapGetters } = createNamespacedHelpers('datasetManager');

export default {
  components: {
    datasetTable: DatasetTable,
    donutChart: DonutChart,
    contentHeader: Header,
  },
  data() {
    return {
      search: '',
      radioGroup: [{ samples: 10 }, { samples: 6 }, { samples: 9 }],
    };
  },
  computed: {
    ...mapGetters({
      selected_datasets: getters.SELECTED_DATASETS,
    }),
  },
};
</script>

<style scoped>
</style>
