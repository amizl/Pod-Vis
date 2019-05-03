<template>
  <transition name="fade" mode="out-in">
    <loading-spinner v-if="isLoading" small />
    <histogram-sparkline
      v-else-if="type === 'observation'"
      :data="data"
      value="value"
    />
    <column-chart v-else :data="data" />
  </transition>
</template>

<script>
import axios from 'axios';
import HistogramSparkline from '@/components/charts/HistogramSparkline.vue';
import ColumnChart from '@/components/charts/ColumnChart.vue';

export default {
  components: {
    HistogramSparkline,
    ColumnChart,
  },
  props: {
    type: {
      type: String,
      required: true,
    },
    scale: {
      type: String,
      required: true,
    },
    datasetId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      isLoading: true,
      data: [],
    };
  },
  async created() {
    this.isLoading = true;
    if (this.type === 'observation') {
      const { data } = await this.fetchObservationVariableCounts();
      this.data = data.counts; // COUNTS NEED TO BE CHANGED...
    } else {
      const { data } = await this.fetchSubjectVariableCounts();
      this.data = data.counts;
    }
    this.isLoading = false;
  },
  methods: {
    fetchObservationVariableCounts() {
      return axios.get(
        `/api/studies/${this.datasetId}/variables/${this.scale}/distribution`
      );
    },
    fetchSubjectVariableCounts() {
      // TODO: Write subject variable counts
      return axios.get(
        `/api/studies/${this.datasetId}/subjects/variables/${
          this.scale
        }/distribution`
      );
    },
  },
};
</script>

<style lang="scss" scoped></style>
