<template>
  <v-card>
    <v-card-title card color="white">
      <p>
        <span class="title">Missing Variables</span> <br />
        <span class="subheading grey--text ligthen-2"
          >These variables are not shared amongst selected datasets.
        </span>
      </p>
    </v-card-title>
    <v-tabs v-model="activeDataset" slider-color="primary">
      <v-tab v-for="dataset in selectedDatasets" :key="dataset.id">
        {{ dataset.study_name }}
      </v-tab>
      <v-tab-item v-for="dataset in selectedDatasets" :key="dataset.id">
        <variable-table :dataset-id="dataset.id" />
      </v-tab-item>
    </v-tabs>
  </v-card>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    id: {
      type: Number,
      required: true,
    },
    studyName: {
      type: String,
      required: true,
    },
    projectName: {
      type: String,
      required: true,
    },
  },
  data: () => ({
    loading: false,
    dataset: {},
    groupBy: ['sex', 'race'],
    summaryData: null,
  }),
  async created() {
    this.loading = true;

    const summary = await this.fetchDemographicSummary();
    const { counts } = summary.data;
    this.summaryData = counts;

    this.loading = false;
  },
  methods: {
    fetchDataset() {
      return axios.get(`/api/studies/${this.id}?include=project`);
    },
    fetchDemographicSummary() {
      // Forms a query similar to group_by=sex&group_by=race
      const queryParams = this.groupBy
        .map(group => `group_by=${group}`)
        .join('&');

      return axios.get(`/api/studies/${this.id}/subjects/count?${queryParams}`);
    },
  },
};
</script>

<style lang="scss" scoped></style>
