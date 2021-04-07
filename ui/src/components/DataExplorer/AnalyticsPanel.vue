<template>
  <v-sheet color="white" class="rounded-lg shadow">
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-sheet color="white" class="rounded-lg shadow">
            <v-container v-if="showTitleBar" fluid fill-width class="ma-0 pa-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <v-card color="#eeeeee" class="pt-1">
                    <v-card-title class="primary--text pl-3 py-2"
                      >{{ title }} &nbsp;

                      <v-tooltip v-if="anovaPvalsInput" top color="primary">
                        <template v-slot:activator="{ on: tooltip }">
                          <span v-on="{ ...tooltip }">{{
                            '(' + anovaPvalsInput.numGroups + ')'
                          }}</span>
                        </template>
                        <span
                          >Statistical analysis was performed with
                          {{ anovaPvalsInput.numGroups }} cohort(s).</span
                        >
                      </v-tooltip>

                      <v-spacer />
                      <span v-if="expanded">
                        <v-chip
                          v-for="(x, index) in [
                            '1',
                            '0.1',
                            '0.05',
                            '0.01',
                            '0.001',
                          ]"
                          :key="`vc1-${index}`"
                          :color="
                            colors['pvals'][x + '-' + colorScheme]['color']
                          "
                          :class="
                            colorScheme == 'brewer5' && x == '0.001'
                              ? 'white--text'
                              : ''
                          "
                          >p &lt; {{ x }}</v-chip
                        ></span
                      >
                      <v-spacer v-if="expanded" />
                      <v-toolbar-items v-if="showTitleBar">
                        <v-icon v-if="expanded" @click="expandClicked(false)"
                          >chevron_left</v-icon
                        >
                        <v-icon v-else @click="expandClicked(true)"
                          >chevron_right</v-icon
                        >
                      </v-toolbar-items>
                    </v-card-title>
                  </v-card>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-col>
      </v-row>

      <v-row v-if="!showTitleBar" class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0" align="center">
          <v-sheet color="white" class="rounded-lg shadow">
            <span v-if="expanded">
              <v-chip
                v-for="(x, index) in ['1', '0.1', '0.05', '0.01', '0.001']"
                :key="`vc2-${index}`"
                :color="colors['pvals'][x + '-' + colorScheme]['color']"
                :class="
                  'px-2 mx-1 ' +
                    (colorScheme == 'brewer5' && x == '0.001'
                      ? 'white--text'
                      : '')
                "
                :style="'border: 2px solid black;'"
                >p &lt; {{ x }}</v-chip
              ></span
            >
          </v-sheet>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-data-table
            ref="ovars_table"
            dense
            :headers="headers"
            :items="ovars"
            item-key="id"
            hide-footer
            sort-by="p_value"
          >
            <template v-slot:item="props">
              <tr
                :key="props.index"
                :class="{ selectedRow: isOVSelected(props.item) }"
                @click="table_row_click(props.item)"
              >
                <td
                  class="text-subtitle-1 text-xs-left"
                  :style="
                    expanded || !colorScaleWhenMinimized
                      ? ''
                      : {
                          backgroundColor: pval_table_cell_color(props.item),
                          color: pval_table_text_color(props.item),
                        }
                  "
                >
                  <v-row align="center">
                    <v-tooltip v-if="showCategoryIcons" bottom color="primary">
                      <template v-slot:activator="{ on: tooltip }">
                        <img
                          :src="
                            '/images/' + props.item.category + '-icon-128.png'
                          "
                          :title="props.item.category"
                          style="height:2em"
                          class="ma-1"
                          v-on="{ ...tooltip }"
                        />
                      </template>
                      <span v-html="props.item.category"></span>
                    </v-tooltip>
                    <v-tooltip v-if="!expanded" bottom color="primary">
                      <template v-slot:activator="{ on: tooltip }">
                        <span
                          v-on="{ ...tooltip }"
                          v-html="props.item.abbreviation"
                        ></span>
                      </template>
                      <span
                        v-html="
                          props.item.label +
                            '  Test: ' +
                            '1-way ANOVA' +
                            '  F-Statistic:' +
                            format_fval(props.item.f_statistic) +
                            '  p-Value:' +
                            format_pval(props.item.p_value)
                        "
                      >
                      </span>
                    </v-tooltip>

                    <v-tooltip v-else top color="primary">
                      <template v-slot:activator="{ on: tooltip }">
                        <span v-on="{ ...tooltip }">
                          {{ props.item.abbreviation }}
                        </span>
                      </template>
                      <span v-html="props.item.label"></span>
                    </v-tooltip>
                  </v-row>
                </td>
                <td v-if="expanded" class="text-subtitle-1 text-xs-left">
                  <v-tooltip bottom color="primary">
                    <template v-slot:activator="{ on: tooltip }">
                      <span v-on="{ ...tooltip }">{{
                        props.item.test_abbrev ? props.item.test_abbrev : '-'
                      }}</span>
                    </template>
                    <span>{{ props.item.test_name }}</span>
                  </v-tooltip>
                </td>
                <td v-if="expanded" class="text-subtitle-1 text-xs-left">
                  {{ format_fval(props.item.f_statistic) }}
                </td>
                <td
                  v-if="expanded"
                  :key="props.item.id"
                  class="text-subtitle-1 text-xs-left"
                  :style="{
                    backgroundColor: pval_table_cell_color(props.item),
                    color: pval_table_text_color(props.item),
                  }"
                >
                  {{ format_pval(props.item.p_value) }}
                </td>
                <td>
                  <v-icon v-if="isOVSelected(props.item)" large
                    >arrow_right_alt</v-icon
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
import { format } from 'd3-format';
import { colors } from '@/utils/colors';

export default {
  components: {},
  props: {
    anovaPvalsInput: {
      type: Object,
      required: true,
    },
    anovaPvals: {
      type: Array,
      required: false,
      default: () => [],
    },
    outcomeVariables: {
      type: Array,
      required: true,
    },
    title: {
      type: String,
      required: false,
      default: 'Analytics',
    },
    showTitleBar: {
      type: Boolean,
      required: false,
      default: true,
    },
    selectedVariable: {
      type: Object,
      required: false,
      default: null,
    },
    autoselectFirstVariable: {
      type: Boolean,
      required: false,
      default: false,
    },
    showCategoryIcons: {
      type: Boolean,
      required: false,
      default: true,
    },
    expanded: {
      type: Boolean,
      required: false,
      default: true,
    },
    colorScaleWhenMinimized: {
      type: Boolean,
      required: false,
      default: true,
    },
    colorScheme: {
      type: String,
      required: false,
      default: 'val100',
    },
  },
  data() {
    return {
      selected: [],
      colors: colors,
      ovars: [],
    };
  },
  computed: {
    headers() {
      var headers = [
        {
          text: 'Variable',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ];
      if (this.expanded) {
        headers.push({
          text: 'Test',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        });
        headers.push({
          text: 'F-Statistic',
          value: 'f_statistic',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        });
        headers.push({
          text: 'p-Value',
          value: 'p_value',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        });
      }
      // extra column to display right-facing arrow/chevron
      headers.push({
        text: '',
        value: '',
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
      });
      return headers;
    },

    pval_dict() {
      const pd = {};
      if (this.anovaPvals != null) {
        this.anovaPvals.forEach(a => {
          pd[a.label] = a;
        });
      }
      return pd;
    },
  },
  watch: {
    anovaPvals() {
      this.update_pvals();
    },
    outcomeVariables() {
      this.update_pvals();
    },
  },
  mounted() {
    this.update_pvals();
    if (this.autoselectFirstVariable && this.selectedVariable == null) {
      if (this.outcomeVariables && this.outcomeVariables.length > 0) {
        var vbest = this.outcomeVariables.sort(function(a, b) {
          return a.p_value - b.p_value;
        })[0];
        this.$emit('variableSelected', vbest);
      }
    }
    if (this.outcomeVariables && this.outcomeVariables.length > 0) {
      this.ovars = this.outcomeVariables;
    }
  },
  methods: {
    format_fval(fv) {
      if (fv == null) {
        return '-';
      }
      return `${format('.2f')(fv)}`;
    },
    format_pval(pval) {
      if (pval == null) {
        return '-';
      }
      if (pval < 0.0001) {
        return '<0.0001';
      }
      return `${format('.4f')(pval)}`;
    },
    variable_fval(ov) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { fval } = pd[ov.label];
        return fval;
      }
      return null;
    },
    variable_pval(ov) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { pval } = pd[ov.label];
        return pval;
      }
      return null;
    },
    get_variable(ov) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        return pd[ov.label];
      }
      return null;
    },
    update_pvals() {
      var ap = this;
      this.outcomeVariables.forEach(v => {
        var ov = ap.get_variable(v);
        if (ov == null) {
          v.p_value = null;
          v.f_statistic = null;
          v.test_name = null;
          v.test_abbrev = null;
        } else {
          v.p_value = ov.pval;
          v.f_statistic = ov.fval;
          v.test_name = ov.test_name;
          v.test_abbrev = ov.test_abbrev;
        }
      });
      this.ovars = [...this.outcomeVariables];
    },
    pval_table_cell_aux(ov, which) {
      const pd = this.pval_dict;
      if (ov.label in pd) {
        const { pval } = pd[ov.label];
        let ccl = this.colors['pvals']['1' + '-' + this.colorScheme][which];
        if (pval < 0.001) {
          ccl = this.colors['pvals']['0.001' + '-' + this.colorScheme][which];
        } else if (pval < 0.01) {
          ccl = this.colors['pvals']['0.01' + '-' + this.colorScheme][which];
        } else if (pval < 0.05) {
          ccl = this.colors['pvals']['0.05' + '-' + this.colorScheme][which];
        } else if (pval < 0.1) {
          ccl = this.colors['pvals']['0.1' + '-' + this.colorScheme][which];
        }
        return ccl;
      }
      return '';
    },
    pval_table_cell_class(ov) {
      return this.pval_table_cell_aux(ov, 'class');
    },
    pval_table_cell_color(ov) {
      return this.pval_table_cell_aux(ov, 'color');
    },
    pval_table_text_color(ov) {
      if (this.colorScheme == 'brewer5') {
        const pd = this.pval_dict;
        if (ov.label in pd) {
          const { pval } = pd[ov.label];
          if (pval < 0.001) {
            return 'white';
          }
        }
      }
      return 'black';
    },
    table_row_click(ov) {
      this.$emit('variableSelected', ov);
    },
    isOVSelected(ov) {
      return this.selectedVariable == ov;
    },
    expandClicked(expand) {
      this.$emit('expandClicked', expand);
    },
  },
};
</script>

<style lang="scss" scoped>
tr.selectedRow {
  background-color: rgb(236, 177, 212);
}
</style>
