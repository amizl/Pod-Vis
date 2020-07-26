<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow pa-0 ma-0">
      <v-app-bar dense flat color="rounded-lg">
        <v-toolbar-title class="primary--text title">
          ANALYTICS PANEL
        </v-toolbar-title>
        <v-divider vertical class="ml-4"></v-divider>
        <v-spacer />
        <!--
        <v-toolbar-items>
          <v-icon v-if="expanded" @click="expandClicked">expand_less</v-icon>
          <v-icon v-else @click="expandClicked">expand_more</v-icon>
        </v-toolbar-items>
 -->
      </v-app-bar>
      <v-divider></v-divider>
      <div v-show="expanded">
        <v-container v-if="!pvals || !pvals.length" fluid fill-height>
	  <v-row>
	    <v-col cols="12">

            <v-subheader class="subheading primary--text text--lighten-4">
              <div v-if="collection.is_longitudinal">
                Add variables and apply filters to them to view statistical test
                results for all outcome variables.
              </div>
              <div v-else>
                Statistical tests for cross-sectional data are not yet
                implemented.
              </div>
            </v-subheader>
            </v-col>
          </v-row>
        </v-container>
        <div v-else>
          <v-toolbar-title class="primary--text title ml-3 mt-2">
            Comparing cohort vs. remainder change:</v-toolbar-title
          >

          <v-container
            align-center
            fluid
            pa-0
            mt-3
            pl-4
            style="border: 4px solid rgb(236,118,188); border-radius: 0.4rem;"
          >
            <v-row class="pa-0 ma-0">
	      <v-col class="pa-0 ma-0">
              <span class="pa-0 mr-1 subtitle-1">Highlight P &lt;</span
              ><v-radio-group v-model="pvt" row>
                <v-radio
                  v-for="pv in pval_thresholds"
                  :label="pv.toString()"
                  :value="pv"
                ></v-radio>
              </v-radio-group>
	      </v-col>
            </v-row>
          </v-container>

          <v-data-table
            :headers="headers"
            :items="pvals"
            dense
            hide-default-footer
            disable-pagination
          >
            <template v-slot:item="props">
              <tr :class="getVariableClass(props.item)">
                <td class="text-subtitle-1 text-xs-left">
                  {{ props.item.label }}
                </td>
                <td
                  class="text-subtitle-1 text-xs-left"
                  :title="props.item.test_name"
                >
                  {{ props.item.test_abbrev }}
                </td>
                <td
                  v-if="props.item.error"
                  class="text-subtitle-1 text-xs-left error"
                  colspan="2"
                >
                  {{ props.item.error }}
                </td>
                <td
                  v-if="!props.item.error"
                  class="text-subtitle-1 text-xs-right"
                  :title="props.item.effect_size_descr"
                >
                  {{ props.item.effect_size | formatEffectSize }}
                </td>
                <td
                  v-if="!props.item.error"
                  class="text-subtitle-1 text-xs-right"
                >
                  {{ props.item.pval | formatPValue }}
                </td>
              </tr>
            </template>
          </v-data-table>
        </div>
      </div>
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
          sortable: true,
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Test',
          align: 'left',
          sortable: true,
          value: 'test_name',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Effect Size',
          align: 'left',
          sortable: true,
          value: 'effect_size',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'P Value',
          align: 'left',
          sortable: true,
          value: 'pval',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
      expanded: true,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      pvals: state.PVALS,
      pval_threshold: state.PVAL_THRESHOLD,
      collection: state.COLLECTION,
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
table.v-data-table thead tr th {
  font-size: 24px;
}
table.v-data-table tbody tr td {
  font-size: 24px;
}

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
