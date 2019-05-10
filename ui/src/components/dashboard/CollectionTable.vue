<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table
    v-else
    :headers="headers"
    :items="collections"
    item-key="label"
    hide-actions
    hide-headers
  >
    <template v-slot:items="props">
      <tr>
        <td class="text-xs-left">{{ props.item.label }}</td>
        <td class="text-xs-right px-0">
          <v-btn flat @click="routeToCohort(props.item)">
            <v-icon left small color="secondary">group_add</v-icon> Create
            Cohort
          </v-btn>
        </td>
      </tr>
    </template>
    <template v-slot:no-data>
      <v-alert :value="true" color="info" icon="info">
        You have no saved collections.
      </v-alert>
    </template>
  </v-data-table>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';

export default {
  data() {
    return {
      headers: [
        {
          text: 'Collection Name',
          value: 'label',
        },
        {
          text: 'Actions',
          value: 'label',
        },
      ],
    };
  },
  computed: {
    ...mapState('datasetManager', {
      isLoading: state.IS_LOADING,
      collections: state.COLLECTIONS,
    }),
  },
  created() {
    if (!this.collections.length) this.fetchDatasets();
  },
  methods: {
    ...mapActions('datasetManager', {
      fetchDatasets: actions.FETCH_COLLECTIONS,
    }),
    routeToCohort({ id }) {
      // Route to view for dataset information
      // const currentPath = this.$router.currentPath.fullPath;
      // this.$router.push(`analysis/${id}/`);
      this.$router.push(`cohorts?collection=${id}`);
    },
  },
};
</script>

<style></style>
