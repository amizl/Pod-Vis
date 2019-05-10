<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table v-else :headers="headers" :items="collections" item-key="label">
    <template v-slot:items="props">
      <tr>
        <td class="text-xs-left">{{ props.item.label }}</td>
        <td class="text-xs-right justify-center">
          <v-tooltip top color="primary">
            <template v-slot:activator="{ on }">
              <v-icon
                color="primary"
                class="mr-1"
                @click="deleteCollection(props.item.id)"
                v-on="on"
                >delete</v-icon
              >
            </template>
            <span>Delete collection</span>
          </v-tooltip>
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
          text: '',
          value: 'name',
          sortable: false,
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
    if (!this.collections.length) this.fetchCollections();
  },
  methods: {
    ...mapActions('datasetManager', {
      fetchCollections: actions.FETCH_COLLECTIONS,
      deleteCollection: actions.DELETE_COLLECTION,
    }),
  },
};
</script>

<style></style>
