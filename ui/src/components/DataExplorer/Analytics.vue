<template>
  <div class="ma-1 pa-0">
    <v-app-bar text dense class="rounded-lg">
      <v-toolbar-title class="title primary--text">
        ANOVA -
        <span class="subtitle-1">1-way ANOVA for first-last visit change</span>
      </v-toolbar-title>
      <v-spacer />
    </v-app-bar>

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
              <tr>
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
    }),
  },
};
</script>

<style lang="scss" scoped></style>
