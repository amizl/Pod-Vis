<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table
    v-else
    :headers="headers"
    :items="this.show_public_collections ? publicCollections : privateCollections"
    item-key="label"
    hide-actions
    hide-headers
  >
    <template v-slot:items="props">
      <tr>
        <td class="text-xs-left">{{ props.item.label }}</td>
        <td class="text-xs-right px-0">

          <v-tooltip top color="primary">
           <template v-slot:activator="{ on }">
	  <v-btn flat @click="routeToCohortManager(props.item)" v-on="on">
            <v-icon left small color="secondary">group_add</v-icon> Cohorts ({{props.item.num_cohorts}})
          </v-btn>
          </template>
          <span>Launch Cohort Manager to add/remove Cohorts</span>
        </v-tooltip>

          <v-tooltip top color="primary">
           <template v-slot:activator="{ on }">
          <v-btn flat @click="routeToDataExplorer(props.item)" :disabled="props.item.num_cohorts == 0" v-on="on">
            <v-icon left small color="secondary">explore</v-icon> Explore
          </v-btn>
          </template>
          <span>Launch Data Explorer to compare Cohorts</span>
        </v-tooltip>

        <delete-collection-button v-if="props.item.is_deletable" :collection_id="props.item.id"/>
	</td>
      </tr>
    </template>
    <template v-slot:no-data>
      <v-alert v-if="show_public_collections" :value="true" color="primary" icon="info">
        There are no public clinical data collections.
      </v-alert>
      <v-alert v-else :value="true" color="primary" icon="info">
        You have no saved clinical data collections.
      </v-alert>
    </template>
  </v-data-table>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import DeleteCollectionButton from '@/components/dashboard/DeleteCollectionBtnDialog';

export default {
  components: {
    DeleteCollectionButton,
  },
  props: {
    // whether to show public collections (and _only_ public collections)
    show_public_collections: {
      type: Boolean,
      required: true,
    },
  },
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
    publicCollections() {
      return this.filterCollections(true);
    },
    privateCollections() {
      return this.filterCollections(false);
    },
  },
  mounted() {
    if (!this.isLoading) {
      this.fetchDatasets();
    }
  },
  methods: {
    ...mapActions('datasetManager', {
      fetchDatasets: actions.FETCH_COLLECTIONS,
      deleteCollection: actions.DELETE_COLLECTION,
    }),
    filterCollections(is_public) {
      var filtered_collections = [];
      this.collections.forEach(function(c) {
        if (c.is_public == is_public) {
            filtered_collections.push(c);
        }
      });
      return filtered_collections;
    },
    routeToCohortManager({ id }) {
      // Route to view for dataset information
      // const currentPath = this.$router.currentPath.fullPath;
      // this.$router.push(`analysis/${id}/`);
      this.$router.push(`cohorts?collection=${id}`);
    },
    routeToDataExplorer({ id }) {
      // Route to view for dataset information
      // const currentPath = this.$router.currentPath.fullPath;
      // this.$router.push(`analysis/${id}/`);
      this.$router.push(`explore?collection=${id}`);
    },
  },
};
</script>

<style></style>
