<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-card-title class="title primary--text">Cohorts</v-card-title>
      <v-divider></v-divider>
      <v-data-table
        v-model="selected"
        flat
        :headers="headers"
        :items="collection_cohorts"
        item-key="id"
        :rows-per-page-items="[5]"
        select-all
      >
        <template v-slot:items="props">
          <td>
            <v-checkbox
              v-model="props.selected"
              primary
              hide-details
            ></v-checkbox>
          </td>
          <td class="text-xs-right">{{ props.item.label }}</td>
        </template>
      </v-data-table>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';

export default {
  data() {
    return {
      selected: [],
      headers: [
        {
          text: 'Cohort',
          align: 'right',
          sortable: true,
          value: 'label',
        },
      ],
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      cohorts: state.COHORTS,
      collection: state.COLLECTION,
    }),

    // cohorts are collection-specific
    collection_cohorts() {
      var cch = [];
      var cid = this.collection.id

      this.cohorts.forEach(function(e) {
        if (e.collection_id === cid) {
          cch.push(e);
        }
      });
      
      return cch;
    },
},
  created() {
    this.fetchCohorts();
  },
  methods: {
    ...mapActions('dataExplorer', {
      fetchCohorts: actions.FETCH_COHORTS,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
