<template>
  <div>
    <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>

    <v-data-table
      :headers="headers"
      :items="visibleCollections"
      item-key="label"
      hide-actions
      disable-initial-sort
    >
      <template v-slot:items="props">
        <tr>
          <td class="text-xs-left">{{ props.item.label }}</td>
          <td class="text-xs-left">
            {{ props.item.date_generated | formatDate }}
          </td>
          <td class="text-xs-left">
            {{ props.item.is_public ? 'Yes' : 'No' }}
          </td>
          <td class="text-xs-left px-0">
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on }">
                <v-btn @click="routeToCohortManager(props.item)" v-on="on">
                  <v-icon left small color="secondary">group_add</v-icon> Add
                  Cohorts ({{ props.item.num_cohorts }})
                </v-btn>
              </template>
              <span class="subtitle-1"
                >Launch Cohort Manager to add/remove Cohorts ({{props.item.num_cohorts}} cohorts created so far)</span
              >
            </v-tooltip>

            <v-tooltip top color="primary">
              <template v-slot:activator="{ on }">
                <v-btn
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

            <v-tooltip top color="primary">
              <template v-slot:activator="{ on }">
                <v-btn
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
        <v-alert :value="true" color="primary" icon="info">
          You have no saved study datasets.
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
  filters: {
    formatDate(ts) {
      // note that toISOString is going to give us UTC
      return new Date(ts).toISOString().substr(0, 10);
    },
  },
  components: {
    DeleteCollectionButton,
  },
  props: {
    // which collections to show - public, private, or all
    showCollections: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      headers: [
        {
          text: 'Study Dataset',
          value: 'label',
        },
        {
          text: 'Created',
          value: 'date_generated_epoch',
        },
        {
          text: 'Public?',
          value: 'is_public',
        },
        {
          text: 'Available Actions',
          value: 'label',
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
    visibleCollections() {
      if (this.showCollections === 'all') {
        return this.collections;
      } else if (this.showCollections === 'public') {
        return this.filterCollections(1);
      } else if (this.showCollections === 'private') {
        return this.filterCollections(0);
      }
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
