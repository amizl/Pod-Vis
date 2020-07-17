<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-card-title class="title primary--text"
        >One-Way ANOVA
        <v-spacer />
        <v-chip color="#FEEDDE">p &lt; 1</v-chip>
        <v-chip color="#FDD0A2">p &lt; 0.1</v-chip>
        <v-chip color="#FDAE6B">p &lt; 0.01</v-chip>
        <v-chip color="#FD8D3C">p &lt; 0.001</v-chip>
        <v-chip color="#F16913">p &lt; 0.0001</v-chip>
      </v-card-title>
      <v-divider></v-divider>

      <v-flex xs12 style="overflow:auto">
        <v-data-table
          dense
          :headers="headers"
          :items="outcomeVariables"
          class="elevation-1"
          :rows-per-page-items="[100]"
          :hide-footer="true"
        >
          <template v-slot:items="props">
            <tr :class="{ selectedRow: isOVSelected(props.item) }">
              <td class=" text-xs-left" @click="table_row_click(props.item)">
                {{ props.item.category }}
              </td>
              <td class="text-xs-left">{{ props.item.label }}</td>
              <td class="text-xs-left">1-way ANOVA</td>
              <td class="text-xs-left">{{ variable_fval(props.item) }}</td>
              <!--

              <td :key="props.item.id">
                <v-layout justify-left
                  ><v-chip
                    class="text-xs-left"
                    :color="table_cell_color(props.item)"
                    @click="table_cell_click(props.item)"
                    >{{ table_cell(props.item) }}</v-chip
                  ></v-layout
                >
              </td>
              -->
              <td
                :key="props.item.id"
                class="text-xs-left"
                :style="{ backgroundColor: table_cell_color(props.item) }"
                @click="table_cell_click(props.item)"
              >
                {{ table_cell(props.item) }}
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-flex>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state as deState } from '@/store/modules/dataExplorer/types';
import { actions, state } from '@/store/modules/analysisSummary/types';
import { format } from 'd3-format';

export default {
  components: {},
  props: {},
  data() {
    return {
      selected: [],
      headers: [
        {
          text: 'Outcome Category',
          value: 'label',
        },
        {
          text: 'Outcome Variable',
          value: 'label',
        },
        {
          text: 'Statistical Test',
          value: 'label',
        },
        {
          text: 'F-Statistic',
          value: 0,
        },
        {
          text: 'p-Value',
          value: 0,
        },
      ],
    };
  },
  computed: {
    ...mapState('analysisSummary', {
      selectedOutcomeVariable: state.SELECTED_OUTCOME_VARIABLE,
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

      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          e.color = { value: '#d0d0d0', text: 'Grey' };
          cch.push(e);
        }
      });

      return cch;
    },
    pval_dict() {
      const ap = this.anova_pvals;
      const pd = {};
      ap.forEach(a => {
        pd[a.label] = a;
      });
      return pd;
    },
    items() {
      return [this.collection_cohorts[0]];
    },
    outcomeVars() {
      return [this.outcomeVariables];
    },
  },
  created() {
    this.setSelectedOutcomeVariable(null);
  },
  methods: {
    ...mapActions('analysisSummary', {
      setSelectedOutcomeVariable: actions.SET_SELECTED_OUTCOME_VARIABLE,
    }),
    variable_fval(ov) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { fval } = pd[ov.label];
        return `${format('.3f')(fval)}`;
      }
      return null;
    },
    variable_pval(ov) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { pval } = pd[ov.label];
        if (pval < 0.0001) {
          return 'p<0.0001';
        }
        return `p=${format('.4f')(pval)}`;
      }
      return null;
    },
    table_cell(ov) {
      let pval = this.variable_pval(ov);
      if (pval === null) {
        return 'X';
      }
      return pval;
    },
    table_cell_class(ov) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { pval } = pd[ov.label];
        let ccl = 'pval-lt-1';
        if (pval < 0.0001) {
          ccl = 'pval-lt-0p001';
        } else if (pval < 0.001) {
          ccl = 'pval-lt-0p01';
        } else if (pval < 0.01) {
          ccl = 'pval-lt-0p05';
        } else if (pval < 0.1) {
          ccl = 'pval-lt-0p1';
        }
        return ccl;
      }
      return '';
    },
    table_cell_color(ov) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { pval } = pd[ov.label];
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
      }
      return '';
    },
    table_row_click(ov) {
      this.setSelectedOutcomeVariable(ov);
    },
    table_cell_click(ov) {
      this.setSelectedOutcomeVariable(ov);
    },
    isOVSelected(ov) {
      if (this.selectedOutcomeVariable == ov) {
        return true;
      }
      return false;
    },
  },
};
</script>

<style lang="scss" scoped></style>
