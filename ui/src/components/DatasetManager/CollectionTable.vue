<template>
  <div>
    <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>

    <v-data-table
      :headers="headers"
      :items="visibleCollections"
      item-key="label"
      disable-pagination
      hide-default-footer
    >
      <template v-slot:item="props">
        <tr>
          <td class="text-subtitle-1 text-xs-left">
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span v-on="{ ...tooltip }">{{ props.item.label }}</span>
              </template>
              <span class="subtitle-1">{{
                getCollectionDescription(props.item)
              }}</span>
            </v-tooltip>
          </td>
          <td class="text-subtitle-1 text-xs-left">
            {{ props.item.date_generated | formatDate }}
          </td>
          <td class="text-subtitle-1 text-xs-left">
            {{ props.item.is_public ? 'Yes' : 'No' }}
          </td>
          <td class="text-subtitle-1 text-xs-left px-0">
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <v-btn
                  small
                  class="mr-2"
                  @click="routeToDataSummary(props.item)"
                  v-on="{ ...tooltip }"
                >
                  Set Visits
                </v-btn>
              </template>
              <span class="subtitle-1"
                >View Data Summary and choose First &amp; Last Visit</span
              >
            </v-tooltip>

            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <v-btn
                  :disabled="!props.item.has_visits_set"
                  small
                  class="mr-2"
                  @click="routeToCohortManager(props.item)"
                  v-on="{ ...tooltip }"
                >
                  <v-icon left small color="secondary">group_add</v-icon> Add
                  Cohorts ({{ props.item.num_cohorts }})
                </v-btn>
              </template>
              <span class="subtitle-1"
                >Launch Cohort Manager to add/remove Cohorts ({{
                  props.item.num_cohorts
                }}
                cohort{{ props.item.num_cohorts > 1 ? 's' : '' }} created so
                far)</span
              >
            </v-tooltip>

            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <v-btn
                  :disabled="props.item.num_cohorts == 0"
                  small
                  class="mr-2"
                  @click="routeToDataExplorer(props.item)"
                  v-on="{ ...tooltip }"
                >
                  <v-icon left small color="secondary">analytics</v-icon> Data
                  Analytics
                </v-btn>
              </template>
              <span class="subtitle-1"
                >Analyze cohorts, predictor variables, and outcomes.</span
              >
            </v-tooltip>

            <delete-collection-button
              v-if="props.item.is_deletable"
              :collection-id="props.item.id"
              :collection-name="props.item.label"
            />
          </td>
          <td class="text-subtitle-1 text-xs-left">
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <v-icon
                  color="primary"
                  class="mr-1"
                  @click="routeToDatasetSummary(props.item.id)"
                  v-on="{ ...tooltip }"
                  >info</v-icon
                >
              </template>
              <span>View dataset summary.</span>
            </v-tooltip>
          </td>
        </tr>
        <tr v-for="(cohort, index) in props.item.cohorts" :key="`ctr-${index}`">
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
import { getCollectionDescription } from '@/utils/helpers';

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
      getCollectionDescription: getCollectionDescription,
      headers: [
        {
          text: 'Study Dataset',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Created',
          value: 'date_generated_epoch',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Public?',
          value: 'is_public',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Available Actions',
          value: 'label',
          sortable: false,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Info',
          value: 'name',
          align: 'left',
          sortable: false,
          class: 'text-subtitle-1 font-weight-bold',
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
      return null;
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
    routeToDataSummary({ id }) {
      this.$router.push(`data_summary?collection=${id}`);
    },
    routeToCohortManager({ id }) {
      this.$router.push(`cohorts?collection=${id}`);
    },
    routeToDataExplorer({ id }) {
      this.$router.push(`explore?collection=${id}`);
    },
    routeToAnalysisSummary({ id }) {
      this.$router.push(`summary?collection=${id}`);
    },
    routeToDatasetSummary(id) {
      this.$router.push(`study_datasets/${id}`);
    },
  },
};
</script>

<style></style>
