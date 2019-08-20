<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-toolbar card dense flat color="white rounded-lg">
        <v-toolbar-title class="subheading primary--text"
          >Mann-Whitney Rank Test</v-toolbar-title
        >
      </v-toolbar>
      <v-divider></v-divider>
      <v-container v-if="!pvals.length" fluid fill-height>
        <v-layout column align-center justify-center fill-height>
          <v-subheader class="subheading primary--text text--lighten-4">
            <v-flex xs6
              ><v-icon large class="primary--text text--lighten-4"
                >info</v-icon
              ></v-flex
            >
            <v-flex>
              Add output variables and filter charts for Mann-Whitney rank test
              on cohort and population samples.
            </v-flex>
          </v-subheader>
        </v-layout>
      </v-container>
      <v-flex v-else>
        <v-data-table
          :headers="headers"
          :items="pvals"
          dense
          hide-default-header
        >
          <template v-slot:items="props">
            <tr>
              <td class="text-xs-left">{{ props.item.label }}</td>
              <td class="text-xs-right">{{ props.item.pval | formatValue }}</td>
            </tr>
          </template>
          <!-- <template v-slot:no-data>
            <v-alert :value="true" color="primary" icon="info">
              Add output variables and filter charts for Mann-Whitney rank test
              on cohort and population samples.
            </v-alert>
          </template> -->
        </v-data-table>
      </v-flex>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
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
      ],
    };
  },
  computed: {
    ...mapState('cohortManager', {
      pvals: state.PVALS,
    }),
  },
};
</script>

<style>
/* Transition effect for changing routes */
.fade-enter-active,
.fade-leave-active {
  transition-duration: 0.3s;
  transition-property: opacity;
  transition-timing-function: ease;
}
.fade-enter,
.fade-leave-active {
  opacity: 0;
}
</style>
