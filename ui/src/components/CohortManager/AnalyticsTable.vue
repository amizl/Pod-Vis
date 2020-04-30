<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-toolbar card dense flat color="rounded-lg">
        <v-toolbar-title class="primary--text title">
          ANALYTICS PANEL
          <!--          Mann-Whitney Rank Test
          <div class="subtitle-1">cohort vs. remainder change</div> -->
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
          <v-toolbar-title class="primary--text title ml-3 mt-2">
            Comparing cohort vs. remainder change:</v-toolbar-title
          >
          <v-data-table
            :headers="headers"
            :items="pvals"
            dense
            hide-default-header
          >
            <template v-slot:items="props">
              <tr :class="getVariableClass(props.item)">
                <td class="text-xs-left">{{ props.item.label }}</td>
                <td class="text-xs-left">{{ props.item.test_name }}</td>
                <td
                  v-if="props.item.error"
                  class="text-xs-left error"
                  colspan="2"
                >
                  {{ props.item.error }}
                </td>
                <td v-if="!props.item.error" class="text-xs-right">
                  {{ props.item.effect_size | formatEffectSize }}
                </td>
                <td v-if="!props.item.error" class="text-xs-right">
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

          <v-container
            align-center
            fluid
            pa-0
            pl-4
            style="border: 4px solid rgb(236,118,188); border-radius: 0.4rem;"
          >
            <v-layout align-center row>
              <span style="padding: 0em 0.5em 0em 0em;">Highlight P &lt;</span
              ><v-radio-group v-model="pvt" row>
                <v-radio
                  v-for="pv in pval_thresholds"
                  :label="pv.toString()"
                  :value="pv"
                ></v-radio>
              </v-radio-group>
            </v-layout>
          </v-container>
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
    formatEffectSize(size) {
      return format('.2f')(size);
    },
  },
  data() {
    return {
      highlight_by_pval: false,
      pval_thresholds: ['None', 0.1, 0.05, 0.01, 0.001, 0.0001],
      pvt: 'None',
      headers: [
        {
          text: 'Variable',
          align: 'left',
          sortable: false,
          value: 'label',
        },
        {
          text: 'Test',
          align: 'left',
          sortable: false,
          value: 'test_name',
        },
        {
          text: 'Effect Size',
          align: 'right',
          sortable: true,
          value: 'effect_size',
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
  watch: {
    pvt(newPvt) {
      this.setPvalThreshold(newPvt);
    },
  },
  created() {
    this.pvt = this.pval_threshold;
  },
  methods: {
    ...mapActions('cohortManager', {
      setPvalThreshold: actions.SET_PVAL_THRESHOLD,
    }),

    updatePval(newPval) {
      this.setPvalThreshold(newPval);
    },
    getVariableClass(v) {
      if (v.pval < this.pval_threshold && !v.error) {
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
