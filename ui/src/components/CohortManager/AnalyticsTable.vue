<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-toolbar card dense flat color="white rounded-lg">
        <v-toolbar-title class="primary--text title">
          Mann-Whitney Rank Test
          <div class="subtitle-1">cohort vs. remainder change</div>
        </v-toolbar-title>
        <v-divider vertical class="ml-4"></v-divider>
        <v-spacer />
        <v-toolbar-items>
          <v-icon v-if="expanded" @click="expandClicked">expand_less</v-icon>
          <v-icon v-else @click="expandClicked">expand_more</v-icon>
        </v-toolbar-items>
      </v-toolbar>
      <v-divider></v-divider>
      <div v-show="expanded">
        <v-container v-if="!pvals.length" fluid fill-height>
          <v-layout column align-center justify-center fill-height>
            <v-subheader class="subheading primary--text text--lighten-4">
              <v-flex>
                Add variables and apply filters to them to view Mann-Whitney
                rank test results for all outcome variables.
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
              <tr :class="getVariableClass(props.item)">
                <td class="text-xs-left">{{ props.item.label }}</td>
                <td class="text-xs-right">
                  {{ props.item.pval | formatPValue }}
                </td>
              </tr>
            </template>
            <!-- <template v-slot:no-data>
            <v-alert :value="true" color="primary" icon="info">
              Add output variables and filter charts for Mann-Whitney rank test
              on cohort and population samples.
            </v-alert>
          </template> -->
          </v-data-table>

          <v-select
            label="Highlight P Value <"
            :items="pval_thresholds"
            box
            :value="pval_threshold"
            @change="updatePval"
          ></v-select>
        </v-flex>
      </div>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
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
  },
  data() {
    return {
      highlight_by_pval: false,
      pval_thresholds: ['None', 0.1, 0.05, 0.01, 0.001, 0.0001],
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
      expanded: true,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      pvals: state.PVALS,
      pval_threshold: state.PVAL_THRESHOLD,
    }),
  },
  methods: {
    ...mapActions('cohortManager', {
      setPvalThreshold: actions.SET_PVAL_THRESHOLD,
    }),
    updatePval(newPval) {
      this.setPvalThreshold(newPval);
    },
    getVariableClass(v) {
      if (v.pval < this.pval_threshold) {
        return 'highlight-var-row';
      }
      return '';
    },
    expandClicked() {
      this.expanded = !this.expanded;
    },
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
