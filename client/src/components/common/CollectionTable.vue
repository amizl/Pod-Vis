<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table v-else :headers="headers" :items="collections" item-key="label">
    <template v-slot:items="props">
      <tr>
        <td class="text-xs-left">{{ props.item.label }}</td>
      </tr>
    </template>
    <template v-slot:no-data>
      <v-alert :value="true" color="info" icon="info">
        You have no saved cohorts.
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
  },
};
</script>

<style></style>
