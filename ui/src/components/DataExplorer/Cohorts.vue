<template>
  <section>
    <v-sheet color="white" height="100%" class="rounded-lg shadow">
      <v-layout column fill-height class="ma-1">
        <v-toolbar card dense flat color="white rounded-lg">
          <span class="title primary--text">Cohorts</span>
          <v-divider vertical class="ml-4"></v-divider>
          <v-spacer />
          <v-toolbar-items>
            <cohort-manager-dialog :collection-id="collection.id" />
          </v-toolbar-items>
        </v-toolbar>

        <v-divider></v-divider>

        <v-container
          v-if="
            typeof cohorts === 'undefined' || collection_cohorts.length === 0
          "
          fluid
          fill-height
        >
          <v-flex>Loading</v-flex>
        </v-container>

        <v-data-table
          v-else
          v-model="selected"
          flat
          dense
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
            <td
              v-if="typeof props.item.subject_ids === 'undefined'"
              class="text-xs-left"
              fill-width
            >
              -
            </td>
            <td v-else class="text-xs-left" fill-width>
              {{ props.item.subject_ids.length }}
            </td>
            <td><v-chip :color="props.item.color" /></td>
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
        '#e41a1c',
        '#377eb8',
        '#4daf4a',
        '#984ea3',
        '#ff7f00',
        '#ffff33',
        '#a65628',
        '#f781bf',
        '#999999',
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
  computed: {
    ...mapState('dataExplorer', {
      cohorts: state.COHORTS,
      visibleCohorts: state.VISIBLE_COHORTS,
      collection: state.COLLECTION,
    }),

    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;
      let ind = 0;
      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          e.color = this.colors[ind];
          ind += 1;
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
    // ensure this.selected consistent with visible
    this.selectCohorts(this.visibleCohorts);
  },
  methods: {
    ...mapActions('dataExplorer', {
      fetchCohorts: actions.FETCH_COHORTS,
      setVisibleCohorts: actions.SET_VISIBLE_COHORTS,
    }),
    colorChange(e) {
      this.$root.$emit('update_detailed_view');
    },
    selectCohorts(cohorts) {
      const current = {};
      this.selected.forEach(s => {
        current[s.id] = 1;
      });
      cohorts.forEach(c => {
        if (!(c.id in current)) {
          current[c.id] = 1;
          this.selected.push(c);
        }
      });
    },
  },
};
</script>

<style lang="scss" scoped></style>
