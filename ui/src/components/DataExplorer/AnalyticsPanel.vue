<template>
  <v-sheet color="white" class="rounded-lg shadow">
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-sheet color="white" class="rounded-lg shadow">
            <v-container fluid fill-width class="ma-0 pa-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <v-card color="#eeeeee" class="pt-1">
                    <v-card-title class="primary--text pl-3 py-2"
                      >{{ title }}
                      <v-spacer />
                      <v-chip :color="colors['pvals']['1']['color']"
                        >p &lt; 1</v-chip
                      >
                      <v-chip :color="colors['pvals']['0.1']['color']"
                        >p &lt; 0.1</v-chip
                      >
                      <v-chip :color="colors['pvals']['0.01']['color']"
                        >p &lt; 0.01</v-chip
                      >
                      <v-chip :color="colors['pvals']['0.001']['color']"
                        >p &lt; 0.001</v-chip
                      >
                      <v-chip :color="colors['pvals']['0.0001']['color']"
                        >p &lt; 0.0001</v-chip
                      >
                    </v-card-title>
                  </v-card>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-data-table
            dense
            :headers="headers"
            :items="outcomeVariables"
            class="elevation-1"
            :hide-footer="true"
          >
            <template v-slot:item="props">
              <tr
                :class="{ selectedRow: isOVSelected(props.item) }"
                @click="table_row_click(props.item)"
              >
                <td class="text-subtitle-1 text-xs-left">
                  {{ props.item.category }}
                </td>
                <td class="text-subtitle-1 text-xs-left">
                  {{ props.item.label }}
                </td>
                <td class="text-subtitle-1 text-xs-left">1-way ANOVA</td>
                <td class="text-subtitle-1 text-xs-left">
                  {{ variable_fval(props.item) }}
                </td>
                <td
                  :key="props.item.id"
                  class="text-subtitle-1 text-xs-left"
                  :style="{ backgroundColor: table_cell_color(props.item) }"
                >
                  {{ table_cell(props.item) }}
                </td>
                <td>
                  <v-icon v-if="isOVSelected(props.item)" large
                    >chevron_right</v-icon
                  >
                </td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state as deState } from '@/store/modules/dataExplorer/types';
import { actions, state } from '@/store/modules/analysisSummary/types';
import { format } from 'd3-format';
import { colors } from '@/utils/colors';

export default {
  components: {},
  props: {
    title: {
      type: String,
      required: false,
      default: 'Analytics',
    },
  },
  data() {
    return {
      selected: [],
      headers: [
        {
          text: 'Category',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Scale',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Statistical Test',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'F-Statistic',
          value: 0,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'p-Value',
          value: 0,
          class: 'text-subtitle-1 font-weight-bold',
        },
        // extra column to display right-facing arrow/chevron
        {
          text: '',
          value: '',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
      colors: colors,
    };
  },
  computed: {
    ...mapState('analysisSummary', {
      selectedOutcomeVariable: state.SELECTED_OUTCOME_VARIABLE,
    }),
    ...mapState('dataExplorer', {
      outcomeVariables: deState.OUTCOME_VARIABLES,
      anova_pvals: deState.ANOVA_PVALS,
    }),
    pval_dict() {
      const ap = this.anova_pvals;
      const pd = {};
      ap.forEach(a => {
        pd[a.label] = a;
      });
      return pd;
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
      return 'X';
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
    table_cell_aux(ov, which) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { pval } = pd[ov.label];
        let ccl = this.colors['pvals']['1'][which];
        if (pval < 0.0001) {
          ccl = this.colors['pvals']['0.0001'][which];
        } else if (pval < 0.001) {
          ccl = this.colors['pvals']['0.001'][which];
        } else if (pval < 0.01) {
          ccl = this.colors['pvals']['0.01'][which];
        } else if (pval < 0.1) {
          ccl = this.colors['pvals']['0.1'][which];
        }
        return ccl;
      }
      return '';
    },
    table_cell_class(ov) {
      return this.table_cell_aux(ov, 'class');
    },
    table_cell_color(ov) {
      return this.table_cell_aux(ov, 'color');
    },
    table_row_click(ov) {
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

<style lang="scss" scoped>
tr.selectedRow {
  background-color: rgb(236, 177, 212);
}
</style>
