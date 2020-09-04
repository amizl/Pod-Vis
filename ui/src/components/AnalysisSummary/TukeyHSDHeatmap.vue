<template>
  <v-sheet color="white" class="rounded-lg shadow">
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
		    <v-chip
		      v-for="x in ['1', '0.1', '0.01', '0.05', '0.001']"
                      :color="colors['pvals'][x + '-' + colorScheme]['color']"
                      >p &lt; {{ x }}</v-chip>
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
                    <span v-if="selectedOutcomeVariable" class="subtitle-1" v-html="selectedOutcomeVariable.label"></span>
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
            :items="collection_cohorts"
            class="elevation-1"
	    hide-default-header
            hide-default-footer
            disable-pagination
	    dense
          >
            <template v-slot:item="props">
              <tr>

                <td
                  v-for="c in collection_cohorts"
                  :key="c.id"
                  :class="'text-subtitle-1 ' + table_cell_class(c, props.item)"
                  align="center"
		  :style="((c == highlight_row) && (props.item == highlight_col)) ? 'border: 1px solid blue;' : 'border: 1px solid white;'"
		  @mouseover="if (c.index < props.item.index) {highlight_cell(c, props.item);}"
		  @mouseleave="unhighlight_cells()"
                >
		  <div v-if="c.index == props.item.index" :class="title_cell_class(c, props.item)">
		    {{ c.label }}
		  </div>
                    <v-tooltip v-if="c.index < props.item.index" bottom color="primary">
                      <template v-slot:activator="{ on: tooltip }">
			<div class="pa-2 py-3" v-on="{ ...tooltip }" @click="table_cell_click(c, props.item)">
			  {{ table_cell(c, props.item) }}
			</div>
		      </template>
		      <span>{{ "Click to view " + c.label + " vs " + props.item.label + " in Data Explorer"}}</span>
		    </v-tooltip>
                </td>
		</v-hover>
		
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
import { colors } from '@/utils/colors';

export default {
  components: {},
  props: {
    colorScheme: {
      type: String,
      required: false,
      default: 'val100',
    },
  },
  data() {
    return {
      pval_dict: {},
      colors: colors,
      highlight_row: null,
      highlight_col: null,
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
          e.index = ccnum;
          ccnum += 1;
          cch.push(e);
        }
      });

      return cch;
    },
    headers() {
      const headers = [
      ];
      const cc = this.collection_cohorts;
      cc.forEach(c => {
        headers.push({
          text: c.id,
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
    table_cell_aux(cohort1, cohort2, which ) {
      const pd = this.pval_dict;
      if (!(cohort1.id in pd) || !(cohort2.id in pd[cohort1.id]))
        return (which == 'color') ? '#FFFFFF' : '';
      const pval = pd[cohort1.id][cohort2.id];
      let ccl = this.colors['pvals']['1' + '-' + this.colorScheme][which];
      if (pval < 0.001) {
        ccl = this.colors['pvals']['0.001' + '-' + this.colorScheme][which];
      } else if (pval < 0.05) {
        ccl = this.colors['pvals']['0.05' + '-' + this.colorScheme][which];
      } else if (pval < 0.01) {
        ccl = this.colors['pvals']['0.01' + '-' + this.colorScheme][which];
      } else if (pval < 0.1) {
        ccl = this.colors['pvals']['0.1' + '-' + this.colorScheme][which];
      }

      return ccl;
    },
   table_cell_color(cohort1, cohort2) {
     return this.table_cell_aux(cohort1, cohort2, 'color');
   },
   table_cell_class(cohort1, cohort2) {
     return this.table_cell_aux(cohort1, cohort2, 'class');
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
   highlight_cell(c1, c2) {
     this.highlight_row = c1;
     this.highlight_col = c2;
   },
   unhighlight_cells() {
     this.highlight_row = null;
     this.highlight_col = null;
   },
   title_cell_class(c1, c2) {
     var cls = "font-weight-medium pa-2 py-3";
     if ((this.highlight_row == c1) || (this.highlight_col == c2)) {
       cls = cls + " accent white--text";
     }
     return cls;
   },
 },
};
</script>

<style lang="scss" scoped>
tbody {
    tr:hover {
	background-color: transparent !important;
    }
}
</style>
