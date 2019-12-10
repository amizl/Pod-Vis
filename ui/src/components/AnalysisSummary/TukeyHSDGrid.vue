<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-card-title class="title primary--text"
        >Tukey Range/HSD Test
        <span v-if="selectedOutcomeVariable"
          >&nbsp; - {{ selectedOutcomeVariable.label }}</span
        >
        <v-spacer />
        <v-chip color="#FEEDDE">p &lt;= 1</v-chip>
        <v-chip color="#FDD0A2">p &lt;= 0.1</v-chip>
        <v-chip color="#FDAE6B">p &lt;= 0.05</v-chip>
        <v-chip color="#FD8D3C">p &lt;= 0.01</v-chip>
        <v-chip color="#F16913">p &lt;= 0.001</v-chip>
      </v-card-title>
      <v-divider></v-divider>

      <v-flex xs12 style="overflow:auto">
        <v-data-table
          v-if="selectedOutcomeVariable && collection_cohorts.length > 2"
          :headers="headers"
          :items="items"
          class="elevation-1"
          :rows-per-page-items="[100]"
          :hide-default-footer="true"
          dense
        >
          <template v-slot:items="props">
            <tr>
              <td class="text-xs-left">{{ props.item.label }}</td>
              <td v-for="c in collection_cohorts" :key="c.id">
                <v-layout justify-center>
                  <v-chip
                    v-if="c.index < props.item.index"
                    :color="table_cell_color(c, props.item)"
                    @click="table_cell_click(c, props.item)"
                    >{{ table_cell(c, props.item) }}</v-chip
                  >
                </v-layout>
              </td>
            </tr>
          </template>
        </v-data-table>
        <v-layout
          v-else-if="collection_cohorts.length < 3"
          column
          align-center
          justify-center
          fill-height
        >
          <v-subheader class="display-1 primary--text text--lighten-5">
            Tukey HSD test requires at least 3 Cohorts.
          </v-subheader>
        </v-layout>
        <v-layout v-else column align-center justify-center fill-height>
          <v-subheader class="display-1 primary--text text--lighten-5">
            Select Outcome Variable from 1-Way ANOVA table above.
          </v-subheader>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/analysisSummary/types';
import { state as deState } from '@/store/modules/dataExplorer/types';
import { format } from 'd3-format';

export default {
  components: {},
  props: {},
  data() {
    return {
      pval_dict: {},
    };
  },
  computed: {
    ...mapState('analysisSummary', {
      selectedOutcomeVariable: state.SELECTED_OUTCOME_VARIABLE,
      pairwiseTukeyHsdPvals: state.PAIRWISE_TUKEY_HSD_PVALS,
    }),
    ...mapState('dataExplorer', {
      cohorts: deState.COHORTS,
      collection: deState.COLLECTION,
      outcomeVariables: deState.OUTCOME_VARIABLES,
      anova_pvals: deState.ANOVA_PVALS,
    }),
    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;
      let ccnum = 0;

      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          e.color = { value: '#d0d0d0', text: 'Grey' };
          e.index = ccnum;
          ccnum += 1;
          cch.push(e);
        }
      });

      return cch;
    },
    headers() {
      const headers = [
        {
          text: '',
          align: 'left',
          sortable: false,
          divider: true,
          value: 'cohort',
        },
      ];
      const cc = this.collection_cohorts;
      cc.forEach(c => {
        headers.push({
          text: c.label,
          align: 'center',
          sortable: false,
          divider: true,
          value: c.label,
        });
      });
      // remove last column
      headers.pop();
      return headers;
    },
    items() {
      const cc = this.collection_cohorts;
      // remove first row
      return cc.slice(1);
    },
  },
  watch: {
    selectedOutcomeVariable() {
      this.update_pval_dict();
    },
  },
  methods: {
    update_pval_dict() {
      const pd = {};
      if (typeof this.selectedOutcomeVariable === 'undefined') return;
      if (this.collection_cohorts.length < 3) return;
      const pvals = this.pairwiseTukeyHsdPvals[
        this.selectedOutcomeVariable.label
      ];
      const groups = pvals.unique_groups;
      const ng = groups.length;
      let ind = 0;
      for (let i = 0; i < ng; i += 1) {
        pd[groups[i]] = {};
        for (let j = i + 1; j < ng; j += 1) {
          pd[groups[i]][groups[j]] = pvals.pvals[ind];
          ind += 1;
        }
      }
      this.pval_dict = pd;
    },
    table_cell(cohort1, cohort2) {
      if (cohort1.index < cohort2.index) {
        const pd = this.pval_dict;
        const pval = pd[cohort1.id][cohort2.id];
        if (pval < 0.0001) {
          return `p=${format('.2e')(pval)}`;
        }
        return `p=${format('.4f')(pval)}`;
      }
      return null;
    },
    table_cell_color(cohort1, cohort2) {
      const pd = this.pval_dict;
      const pval = pd[cohort1.id][cohort2.id];
      let ccl = '#FEEDDE';
      if (pval <= 0.001) {
        ccl = '#F16913';
      } else if (pval <= 0.01) {
        ccl = '#FD8D3C';
      } else if (pval <= 0.05) {
        ccl = '#FDAE6B';
      } else if (pval <= 0.1) {
        ccl = '#FDD0A2';
      }
      return ccl;
    },
    table_cell_click(cohort1, cohort2) {},
  },
};
</script>

<style lang="scss" scoped></style>
