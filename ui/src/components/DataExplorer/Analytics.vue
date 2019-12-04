<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-card-title class="primary--text"
        >ANOVA
        <div class="subheading">1-way ANOVA for first-last visit change</div>
      </v-card-title>
      <v-divider></v-divider>
      <v-container
        v-if="typeof anova_pvals === undefined || !anova_pvals.length"
        fluid
        fill-height
      >
        <v-layout column align-center justify-center fill-height>
          <v-subheader class="subheading primary--text text--lighten-4">
            <v-flex xs6
              ><v-icon large class="primary--text text--lighten-4"
                >info</v-icon
              ></v-flex
            >
            <v-flex> Nothing to show. </v-flex>
          </v-subheader>
        </v-layout>
      </v-container>

      <v-flex v-else>
        <v-data-table
          :headers="headers"
          :items="anova_pvals"
          dense
          hide-default-header
        >
          <template v-slot:items="props">
            <tr>
              <td class="text-xs-left">{{ props.item.label }}</td>
              <td class="text-xs-right">{{ props.item.pval | formatValue }}</td>
              <td class="text-xs-right">{{ props.item.fval | formatValue }}</td>
            </tr>
          </template>
        </v-data-table>
      </v-flex>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';
import { format } from 'd3-format';

export default {
  filters: {
    formatValue(pvalue) {
      return format('.5f')(pvalue);
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
        },
        {
          text: 'P Value',
          align: 'right',
          sortable: true,
          value: 'pval',
        },
        {
          text: 'F Value',
          align: 'right',
          sortable: true,
          value: 'fval',
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
