<template>
  <v-sheet
    :color="this.selectedOutcomeVariable != null ? 'rgb(236,177,212)' : 'white'"
    class="rounded-lg shadow"
  >
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-container fluid fill-width class="ma-0 pa-0">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-card color="#eeeeee" class="pt-1">
                  <v-card-title class="primary--text pl-3 py-2"
                    >Tukey Range/HSD Test
                    <v-spacer />
                    <v-chip color="#FEEDDE">p &lt; 1</v-chip>
                    <v-chip color="#FDD0A2">p &lt; 0.1</v-chip>
                    <v-chip color="#FDAE6B">p &lt; 0.01</v-chip>
                    <v-chip color="#FD8D3C">p &lt; 0.001</v-chip>
                    <v-chip color="#F16913">p &lt; 0.0001</v-chip>
                  </v-card-title>
                  <v-card-title class="primary--text pa-0 pl-3">
                    <v-tooltip
                      v-if="selectedOutcomeVariable"
                      bottom
                      color="primary"
                    >
                      <template v-slot:activator="{ on: tooltip }">
                        <img
                          :src="
                            '/images/' +
                              selectedOutcomeVariable.category +
                              '-icon-128.png'
                          "
                          :title="selectedOutcomeVariable.category"
                          style="height:1.75em"
                          class="ma-1"
                          v-on="{ ...tooltip }"
                        />
                      </template>
                      <span>{{ selectedOutcomeVariable.category }}</span>
                    </v-tooltip>
                    <span v-if="selectedOutcomeVariable" class="subtitle-1">
                      {{ selectedOutcomeVariable.label }}
                    </span>
                  </v-card-title>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-data-table
            v-if="selectedOutcomeVariable && collection_cohorts.length > 2"
            :headers="headers"
            :items="items"
            class="elevation-1"
            hide-default-footer
            disable-pagination
            dense
          >
            <template v-slot:item="props">
              <tr>
                <td class="text-subtitle-1 text-xs-left">
                  {{ props.item.label }}
                </td>
                <td
                  v-for="c in collection_cohorts"
                  :key="c.id"
                  class="text-subtitle-1"
                  align="center"
                >
                  <v-chip
                    v-if="c.index < props.item.index"
                    :color="table_cell_color(c, props.item)"
                    @click="table_cell_click(c, props.item)"
                    >{{ table_cell(c, props.item) }}</v-chip
                  >
                </td>
              </tr>
            </template>
          </v-data-table>

          <div
            v-else-if="collection_cohorts.length < 3"
            column
            align-center
            justify-center
            fill-height
          >
            <v-subheader class="title primary--text text--lighten-5">
              Tukey HSD test requires at least 3 Cohorts.
            </v-subheader>
          </div>
          <div v-else column align-center justify-center fill-width>
            <v-subheader class="title primary--text text--lighten-5">
              Select Variable from One-Way ANOVA table.
            </v-subheader>
          </div>
        </v-col>
      </v-row>
    </v-container>
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
      selectedCohorts: state.SELECTED_COHORTS,
      selectedOutcomeVariable: state.SELECTED_OUTCOME_VARIABLE,
      pairwiseTukeyHsdPvals: state.PAIRWISE_TUKEY_HSD_PVALS,
    }),
    ...mapState('dataExplorer', {
      collection: deState.COLLECTION,
      outcomeVariables: deState.OUTCOME_VARIABLES,
      anova_pvals: deState.ANOVA_PVALS,
    }),
    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;
      let ccnum = 0;

      this.selectedCohorts.forEach(e => {
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
          class: 'text-subtitle-1 font-weight-bold',
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
          class: 'text-subtitle-1 font-weight-bold',
        });
      });
      // remove last column
      //      headers.pop();
      return headers;
    },
    items() {
      const cc = this.collection_cohorts;
      // remove first row
      //      return cc.slice(1);
      return cc;
    },
  },
  watch: {
    selectedOutcomeVariable(nv) {
      this.update_pval_dict();
    },
  },
  methods: {
    update_pval_dict() {
      const pd = {};
      if (
        !this.selectedOutcomeVariable ||
        typeof this.selectedOutcomeVariable === 'undefined'
      )
        return;
      if (this.collection_cohorts.length < 3) return;
      if (!(this.selectedOutcomeVariable.label in this.pairwiseTukeyHsdPvals)) {
        console.log(
          'No results found for ' + this.selectedOutcomeVariable.label
        );
        this.pval_dict = {};
        return;
      }
      const pvals = this.pairwiseTukeyHsdPvals[
        this.selectedOutcomeVariable.label
      ];
      const groups = pvals.unique_groups;
      const ng = groups.length;
      let ind = 0;
      for (let i = 0; i < ng; i += 1) {
        pd[groups[i]] = {};
        for (let j = i + 1; j < ng; j += 1) {
          pd[groups[i]][groups[j]] = pvals == null ? 'x' : pvals.pvals[ind];
          ind += 1;
        }
      }
      this.pval_dict = pd;
    },
    table_cell(cohort1, cohort2) {
      if (cohort1.index < cohort2.index) {
        const pd = this.pval_dict;
        if (!(cohort1.id in pd) || !(cohort2.id in pd[cohort1.id])) return null;
        const pval = pd[cohort1.id][cohort2.id];
        if (pval < 0.0001) {
          return 'p<0.0001';
        }
        return `p=${format('.4f')(pval)}`;
      }
      return null;
    },
    table_cell_color(cohort1, cohort2) {
      const pd = this.pval_dict;
      if (!(cohort1.id in pd) || !(cohort2.id in pd[cohort1.id]))
        return '#FFFFFF';
      const pval = pd[cohort1.id][cohort2.id];
      let ccl = '#FEEDDE';
      if (pval < 0.0001) {
        ccl = '#F16913';
      } else if (pval < 0.001) {
        ccl = '#FD8D3C';
      } else if (pval < 0.01) {
        ccl = '#FDAE6B';
      } else if (pval < 0.1) {
        ccl = '#FDD0A2';
      }
      return ccl;
    },
    table_cell_click(cohort1, cohort2) {
      const cid = this.collection.id;
      var de_url =
        'explore?collection=' +
        cid +
        '&variable=' +
        this.selectedOutcomeVariable.id +
        '&cohorts=' +
        this.selectedCohorts.map(c => c.id).join(',') +
        '&visibleCohorts=' +
        [cohort1.id, cohort2.id].join(',');
      this.$router.push(de_url);
    },
  },
};
</script>

<style lang="scss" scoped></style>
