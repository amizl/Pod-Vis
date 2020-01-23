<template>
  <div>
    <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>

    <v-data-table
      :headers="headers"
      :items="showPublicCollections ? publicCollections : privateCollections"
      item-key="label"
      hide-headers
      hide-actions
    >
      <template v-slot:items="props">
        <tr>
          <td class="text-xs-left">{{ props.item.label }}</td>
          <td class="text-xs-left">{{ props.item.date_generated }}</td>
          <td class="text-xs-right px-0">
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on }">
                <v-btn flat @click="routeToCohortManager(props.item)" v-on="on">
                  <v-icon left small color="secondary">group_add</v-icon> Add
                  Cohorts ({{ props.item.num_cohorts }})
                </v-btn>
              </template>
              <span class="subtitle-1"
                >Launch Cohort Manager to add/remove Cohorts</span
              >
            </v-tooltip>

            <v-tooltip top color="primary">
              <template v-slot:activator="{ on }">
                <v-btn
                  flat
                  :disabled="props.item.num_cohorts == 0"
                  @click="routeToDataExplorer(props.item)"
                  v-on="on"
                >
                  <v-icon left small color="secondary">explore</v-icon> Explore
                </v-btn>
              </template>
              <span class="subtitle-1"
                >Launch Data Explorer to compare Cohorts</span
              >
            </v-tooltip>

            <v-tooltip top color="primary">
              <template v-slot:activator="{ on }">
                <v-btn
                  flat
                  :disabled="props.item.num_cohorts == 0"
                  @click="routeToAnalysisSummary(props.item)"
                  v-on="on"
                >
                  <v-icon left small color="secondary">grid_on</v-icon>
                  Summarize
                </v-btn>
              </template>
              <span class="subtitle-1"
                >View Analysis Summary for current Cohorts</span
              >
            </v-tooltip>

            <delete-collection-button
              v-if="props.item.is_deletable"
              :collection-id="props.item.id"
            />
          </td>
        </tr>
        <tr v-for="(cohort, index) in props.item.cohorts">
          <td colspan="3">cohort row</td>
        </tr>
      </template>
      <template v-slot:no-data>
        <v-alert
          v-if="showPublicCollections"
          :value="true"
          color="primary"
          icon="info"
        >
          There are no public clinical data collections.
        </v-alert>
        <v-alert v-else :value="true" color="primary" icon="info">
          You have no saved clinical data collections.
        </v-alert>
      </template>
    </v-data-table>
  </div>
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
    showPublicCollections: {
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
          text: 'Created',
          value: 'date_generated',
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
      return this.filterCollections(1);
    },
    privateCollections() {
      return this.filterCollections(0);
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
    filterCollections(isPublic) {
      const filteredCollections = [];
      this.collections.forEach(c => {
        if (c.is_public === isPublic) {
          filteredCollections.push(c);
        }
      });
      return filteredCollections;
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
    routeToAnalysisSummary({ id }) {
      // Route to view for analysis summary
      this.$router.push(`summary?collection=${id}`);
    },
  },
};
</script>

<style></style>
