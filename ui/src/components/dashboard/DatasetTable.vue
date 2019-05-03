<template>
  <v-card>
    <v-card-title primary-title class="title"> My Datasets </v-card-title>
    <v-data-table
      :headers="headers"
      :items="datasets"
      hide-actions
      hide-headers
    >
      <template slot="items" slot-scope="props">
        <td>{{ props.item.dataset }}</td>
        <td class="text-xs-right px-0">
          <v-btn flat @click="routeToExplorer(props.item)">
            <v-icon left small color="secondary">bar_chart</v-icon>
            Analyze
          </v-btn>
          <v-btn flat @click="routeToCohort(props.item)">
            <v-icon left small color="secondary">group_add</v-icon> Build Cohort
          </v-btn>
        </td>
      </template>
      <template slot="no-data">
        <td class="text-xs-center">
          Your dashboard is empty. Add datasets to your dashboard in the dataset
          manager.
        </td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dashboard/types';

export default {
  data() {
    return {
      headers: [
        {
          text: 'Dataset',
          align: 'left',
          sortable: false,
          value: 'name',
        },
        {
          text: '',
          align: 'right',
          sortable: false,
          value: 'actions',
        },
      ],
    };
  },
  computed: {
    ...mapState('dashboard', {
      datasets: state.DATASETS,
    }),
  },
  methods: {
    // routeToExplorer({ dataset, id }) {
    routeToExplorer() {
      // Route to view for dataset information
      // const currentPath = this.$router.currentPath.fullPath;
      // this.$router.push(`analysis/${id}/`);
      this.$router.push(`analysis/`);
    },
    routeToCohort({ id }) {
      // Route to view for dataset information
      // const currentPath = this.$router.currentPath.fullPath;
      // this.$router.push(`analysis/${id}/`);
      this.$router.push(`cohorts/build?id=${id}`);
    },
  },
};
</script>

<style lang="stylus" scoped></style>
