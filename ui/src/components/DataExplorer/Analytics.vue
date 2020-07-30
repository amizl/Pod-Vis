<template>
  <div class="ma-0 pa-0">
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2">
              ANOVA -
              <span class="subtitle-1"
                >1-way ANOVA for first-last visit change</span
              >
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-container
      v-if="typeof anova_pvals === undefined || !anova_pvals.length"
      fluid
      fill-width
      class="pa-0 ma-0 pt-2 pl-2"
    >
      <v-row class="pl-2" align="center">
        <v-col cols="12"> Nothing to show. </v-col>
      </v-row>
    </v-container>

    <v-container v-else fluid fill-width class="pa-0 ma-0 pt-2">
      <v-row class="pa-0 ma-0" align="center">
        <v-col cols="12" class="pa-0 ma-0">
          <v-data-table :headers="headers" :items="anova_pvals" dense>
            <template v-slot:item="props">
              <tr
                :class="{
                  selectedRow: detailed_view.label == props.item.label,
                }"
              >
                <td class="text-subtitle-1 text-xs-left">
                  {{ props.item.label }}
                </td>
                <td class="text-subtitle-1 text-xs-right">
                  {{ props.item.pval | formatPValue }}
                </td>
                <td class="text-subtitle-1 text-xs-right">
                  {{ props.item.fval | formatFValue }}
                </td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';
import { format } from 'd3-format';

export default {
  filters: {
    formatPValue(pvalue) {
      if (pvalue < 0.0001) {
        return '< 0.0001';
      } else {
        return format('.4f')(pvalue);
      }
    },
    formatFValue(fvalue) {
      return format('.2f')(fvalue);
    },
  },
  data() {
    return {
      headers: [
        {
          text: 'Variable',
          align: 'left',
          sortable: false,
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'P Value',
          align: 'left',
          sortable: true,
          value: 'pval',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'F Value',
          align: 'left',
          sortable: true,
          value: 'fval',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      anova_pvals: state.ANOVA_PVALS,
      detailed_view: state.DETAILED_VIEW,
    }),
  },
};
</script>

<style lang="scss" scoped>
tr.selectedRow {
  background-color: rgb(236, 177, 212);
}
</style>
