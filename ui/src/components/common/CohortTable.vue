<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <div v-else>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              >Cohorts
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-data-table
      :headers="headers"
      :items="collection_cohorts"
      item-key="id"
      dense
    >
      <template v-slot:item="props">
        <tr>
          <td>
            <v-simple-checkbox
              v-model="props.selected"
              primary
              hide-details
            ></v-simple-checkbox>
          </td>
          <td class="text-subtitle-1 text-xs-left">{{ props.item.label }}</td>
          <td class="text-subtitle-1 text-xs-left">
            {{ props.item.subject_ids.length }}
          </td>
          <td class="text-subtitle-1 text-xs-left">
            {{ props.item.query_string }}
          </td>
        </tr>
      </template>
      <template v-slot:no-data>
        <v-alert :value="true" color="info" icon="info">
          You have no saved cohorts.
        </v-alert>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/dataExplorer/types';

export default {
  data() {
    return {
      selected: [],
      headers: [
        {
          text: 'Select',
          value: 0,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Cohort Name',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Cohort Count',
          value: 0,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Query',
          value: 'query_string',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      isLoading: state.IS_LOADING,
      collection: state.COLLECTION,
      cohorts: state.COHORTS,
    }),

    // cohorts are collection-specific
    collection_cohorts() {
      // include a default select that serves as the new cohort option
      const cch = [];
      const cid = this.collection.id;

      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          cch.push(e);
        }
      });
      return cch;
    },
  },
  watch: {
    selected() {
      const selectedCohorts = {};
      const visibleCohorts = [];
      this.selected.forEach(s => {
        selectedCohorts[s.id] = 1;
      });
      this.cohorts.forEach(c => {
        if (c.id in selectedCohorts) {
          visibleCohorts.push(c);
        }
      });
      this.setVisibleCohorts(visibleCohorts);
    },
  },
  methods: {},
};
</script>

<style></style>
