<template>
  <div>
    <v-app-bar dense text class="rounded-lg">
      <v-toolbar-title class="primary--text title"> Cohorts </v-toolbar-title>
      <v-spacer />
      <v-toolbar-items>
        <cohort-manager-dialog :collection-id="collection.id" />
        <v-icon v-if="expanded" @click="expanded = false">expand_less</v-icon>
        <v-icon v-else @click="expanded = true">expand_more</v-icon>
      </v-toolbar-items>
    </v-app-bar>

    <v-container
      v-if="typeof cohorts === 'undefined' || collection_cohorts.length === 0"
      fluid
      fill-height
    >
      <v-flex>Loading</v-flex>
    </v-container>

    <v-container
      v-else
      v-show="expanded"
      fluid
      fill-height
      class="pa-0 pl-3 pt-3"
    >
      <v-row>
        <v-col cols="12">
          <v-data-table
            v-model="selected"
            dense
            text
            :headers="headers"
            :items="collection_cohorts"
            item-key="id"
            show-select
          >
            <template v-slot:item.label="{ item }">
              <td class="subtitle-1 text-xs-left">{{ item.label }}</td>
            </template>

            <template v-slot:item.subject_ids.length="{ item }">
              <td class="subtitle-1 text-xs-center">
                {{ item.subject_ids.length }}
              </td>
            </template>

            <template v-slot:item.color="{ item }">
              <td class="text-xs-left">
                <v-chip small :color="item.color" class="my-1" />
              </td>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
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
      expanded: true,
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
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Size',
          align: 'left',
          sortable: true,
          value: 'subject_ids.length',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Color',
          align: 'left',
          sortable: false,
          value: 'color',
          class: 'text-subtitle-1 font-weight-bold',
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
    selected(newsel) {
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
