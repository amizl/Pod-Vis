<template>
  <loading-spinner v-if="isLoading" small />
  <v-sparkline v-else :value="value" :label="count" />
</template>

<script>
import axios from 'axios';

export default {
  props: {
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
      value: [],
      count: [],
    };
  },
  async created() {
    const {
      data: { observations },
    } = await axios.get(
      `/api/studies/${this.datasetId}/variables/${this.scale}/distribution`
    );
    this.value = observations.map(obsv => obsv.count);
    this.label = observations.map(obsv => obsv.value);

    this.isLoading = false;
  },
};
</script>

<style lang="scss" scoped></style>
