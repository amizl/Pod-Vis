<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table
    v-else
    :headers="headers"
    :items="collection_cohorts"
    item-key="id"
  >
    <template v-slot:items="props">
      <tr>
        <td>
          <v-checkbox
            v-model="props.selected"
            primary
            hide-details
          ></v-checkbox>
        </td>
        <td class="text-xs-left">{{ props.item.label }}</td>
        <td class="text-xs-left">{{ props.item.subject_ids.length }}</td>
        <td class="text-xs-left">{{ props.item.query_string }}</td>
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
import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  data() {
    return {
      selected: [],
      headers: [
        {
          text: 'Select',
          value: 0,
        },
        {
          text: 'Cohort Name',
          value: 'label',
        },
        {
          text: 'Cohort Count',
          value: 0,
        },
        {
          text: 'Query',
          value: 'query_string',
        },
      ],
    };
  },
  computed: {
    ...mapState('cohortManager', {
      isLoading: state.IS_LOADING,
      cohorts: state.COHORTS,
      collection: state.COLLECTION,
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
  created() {
    if (!this.cohorts.length) this.fetchCohorts();
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCohorts: actions.FETCH_COHORTS,
    }),
  },
};
</script>

<style></style>
