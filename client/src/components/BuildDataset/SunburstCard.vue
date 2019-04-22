<template>
  <v-card>
    <v-card-title primary-title>
      <span class="subheading">
        {{ studyName }} <br />
        <span class="caption grey--text lighten-2"> {{ projectName }} </span>
      </span>
    </v-card-title>
    <loading-spinner v-if="loading" medium></loading-spinner>
    <v-card-text v-else>
      <sunburst-chart :data="summaryData" :keyorder="groupBy">
        <sunburst-legend
          slot="legend"
          slot-scope="{ data, color, actions, nodes }"
          :data="data"
          :color="color"
          :actions="actions"
          :nodes="nodes"
        ></sunburst-legend>
      </sunburst-chart>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn :to="`/datasets/${id}`" flat icon>
        <v-tooltip top color="primary">
          <v-icon slot="activator"> info </v-icon>
          <span>Learn more about this study</span>
        </v-tooltip>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import axios from 'axios';
import SunburstChart from '@/components/charts/sunburst/SunburstChart.vue';
import SunburstLegend from '@/components/charts/sunburst/SunburstLegend.vue';

export default {
  components: {
    SunburstChart,
    SunburstLegend,
  },
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
