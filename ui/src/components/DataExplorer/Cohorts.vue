<template>
  <section>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">

    <v-toolbar card dense flat color="white rounded-lg">
      <span class="title primary--text">Cohorts</span>
      <v-divider vertical class="ml-4"></v-divider>
      <v-spacer />
      <v-toolbar-items> <cohort-manager-dialog :collection_id="this.collection.id" /> </v-toolbar-items>
    </v-toolbar>
    
      <v-divider></v-divider>

      <v-container v-if="collection_cohorts.length === 0" fluid fill-height>
        <v-flex>Loading</v-flex>
      </v-container>

      <v-data-table v-else
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
          <td class="text-xs-left" fill-width>{{ props.item.label }}</td>
          <td v-if="typeof(props.item.subject_ids) === 'undefined'" class="text-xs-left" fill-width>-</td>
          <td v-else class="text-xs-left" fill-width>{{ props.item.subject_ids.length }}</td>
	  <td>
	    <v-select outlined v-model="props.item.color" :items="colors" v-on:change="colorChange"></v-select>
	  </td>
        </template>
      </v-data-table>
    </v-layout>
  </v-sheet>
  </section>
</template>

<script>
import CohortManagerDialog from '@/components/DataExplorer/CohortManagerDialog.vue';
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';

export default {
  components: {
    CohortManagerDialog,
  },
  data() {
    return {
      selected: [],
      colors: [
        { "value": "#dc143c", "text": "Red" },
        { "value": "#143cdc", "text": "Blue" },
        { "value": "#143c3c", "text": "Green" },
        { "value": "#d0d0d0", "text": "Grey" },
      ],
      headers: [
        {
          text: 'Cohort',
          align: 'left',
          sortable: true,
          value: 'label',
        },
        {
          text: 'Size',
          align: 'left',
          sortable: true,
          value: 'subject_ids.length',
        },
        {
          text: 'Color',
          align: 'left',
          sortable: false,
          value: 'color',
        },

      ],
    };
  },
  watch: {
   selected() {
     var selected_cohorts = {};
     var visible_cohorts = [];
     this.selected.forEach(function(s) { selected_cohorts[s['id']] = 1; });
     this.cohorts.forEach(function(c) { if (c.id in selected_cohorts) { visible_cohorts.push(c); }});
     this.setVisibleCohorts(visible_cohorts);
    },
    collection_cohorts() {
     this.setVisibleCohorts(this.visible_cohorts);
    }
  },
  computed: {
    ...mapState('dataExplorer', {
      cohorts: state.COHORTS,
      visible_cohorts: state.VISIBLE_COHORTS,
      collection: state.COLLECTION,
    }),

    // cohorts are collection-specific
    collection_cohorts() {
      var cch = [];
      var cid = this.collection.id

      this.cohorts.forEach(function(e) {
      if (e.collection_id === cid) {
          e['color'] = { "value": "#d0d0d0", "text": "Grey" };
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
      setVisibleCohorts: actions.SET_VISIBLE_COHORTS,
    }),
    colorChange(e) {
      console.log("colorChange - " + e);
      this.$root.$emit('update_detailed_view');
    },
  },
};
</script>

<style lang="scss" scoped></style>
