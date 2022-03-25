<template>
  <div>
    <v-container v-if="showTitleBar" fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              >{{ title }}

              <v-divider vertical class="ml-4 mr-4"> </v-divider>

              <v-tooltip bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <v-chip
                      label
                      color="primary"
                      class="white--text title mr-2"
                      >{{ cohorts.length }}</v-chip
                    >
                    <span class="black--text text-body-1"
                      >Study group{{ cohorts.length == 1 ? '' : 's' }}</span
                    >
                  </span>
                </template>
                <span class="subtitle-1">
                  {{ cohorts.length }} Study group{{
                    cohorts.length == 1 ? '' : 's'
                  }}
                </span>
              </v-tooltip>

              <v-divider v-if="showSelect" vertical class="ml-4 mr-4">
              </v-divider>

              <v-tooltip v-if="showSelect" bottom color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <v-chip
                      label
                      color="primary"
                      class="white--text title mr-2"
                      >{{ selected.length }}</v-chip
                    >
                    <span class="black--text text-body-1">Selected</span>
                  </span>
                </template>
                <span class="subtitle-1">
                  {{ selected.length }} Study group{{
                    selected.length == 1 ? '' : 's'
                  }}
                  selected
                </span>
              </v-tooltip>

              <v-spacer />
              <v-toolbar-items>
                <v-icon v-if="expandedVert" @click="expandedVert = false"
                  >expand_less</v-icon
                >
                <v-icon v-else @click="expandedVert = true">expand_more</v-icon>
              </v-toolbar-items>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-sheet v-show="expandedVert" color="white" class="rounded-lg shadow">
      <!-- no cohorts selected -->
      <v-container
        v-if="!cohorts || cohorts.length == 0"
        fluid
        fill-width
        class="ma-0 pa-0"
      >
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <div column align-center justify-center fill-width class="py-3">
              <v-subheader class="title primary--text text--lighten-5">
                No study groups selected.
              </v-subheader>
            </div>
          </v-col>
        </v-row>
      </v-container>

      <!-- cohorts selected -->
      <v-data-table
        v-else
        v-model="selected"
        :headers="headers"
        :items="cohorts"
        item-key="id"
        :show-select="showSelect"
        :disable-pagination="disablePagination"
        :hide-default-footer="disablePagination"
        dense
      >
        <!-- Add "All:" to select all checkbox -->
        <template v-slot:header.data-table-select="{ on, props }">
          <v-tooltip top color="primary">
            <template v-slot:activator="{ on: tooltip }">
              <span
                class="text-subtitle-1 font-weight-bold"
                v-on="{ ...tooltip }"
              >
                All: <v-simple-checkbox v-bind="props" v-on="on"
              /></span>
            </template>
            <span>Click to select all study groups.</span>
          </v-tooltip>
        </template>

        <template v-slot:item.data-table-select="{ isSelected, select }">
          <td class="pa-0 ma-0" justify="center" align="center">
            <v-tooltip v-if="checkboxTooltip" bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <v-simple-checkbox
                  :value="isSelected"
                  class="pa-0 ma-0"
                  dense
                  hide-details
                  v-on="{ ...tooltip }"
                  @input="select($event)"
                />
              </template>
              <span>{{ checkboxTooltip }}</span>
            </v-tooltip>
            <v-simple-checkbox
              v-else
              :value="isSelected"
              class="pa-0 ma-0"
              dense
              hide-details
              @input="select($event)"
            />
          </td>
        </template>

        <template v-slot:item.label="{ item }">
          <td class="subtitle-1 text-xs-left">
            <span v-html="item.label"></span>
          </td>
        </template>

        <template v-slot:item.size="{ item }">
          <td class="subtitle-1 text-xs-left">
            {{ item.subject_ids ? item.subject_ids.length : '?' }}
          </td>
        </template>

        <template v-slot:item.query_string="{ item }">
          <td class="subtitle-1 text-xs-left">{{ item.query_string }}</td>
        </template>

        <template v-slot:item.color="{ item }">
          <v-tooltip top color="primary">
            <template v-slot:activator="{ on: tooltip }">
              <svg
                width="50"
                height="25"
                class="mt-1"
                v-on="{ ...tooltip }"
                @click="openColorPickerDialog(item)"
              >
                <g>
                  <rect
                    x="0"
                    y="0"
                    rx="0"
                    ry="0"
                    border-radius="0%"
                    width="50"
                    height="25"
                    :fill="item['color']"
                    stroke="black"
                  />
                  <rect
                    v-if="item['pattern'] != null"
                    x="0"
                    y="0"
                    rx="0"
                    ry="0"
                    border-radius="0%"
                    width="50"
                    height="25"
                    :fill="'url(#' + item['pattern']['id'] + ')'"
                    opacity="0.25"
                  />
                </g>
              </svg>

            </template>
            <span
              >Click to change color/pattern for study group '{{
                item.label
              }}'</span
            >
          </v-tooltip>
        </template>
      </v-data-table>

      <div
        v-if="reportMaxOverlap || reportMaxSelectedOverlap"
        class="ma-0 pa-3"
        style="height: 3em"
      >
        <div v-if="reportMaxOverlap && maxOverlap" class="pa-0">
          <v-icon class="pa-1" color="warning" medium>warning</v-icon>
          <span>{{ 'WARNING: ' + maxOverlap.descr }}</span>
        </div>
        <div v-if="reportMaxSelectedOverlap && maxSelectedOverlap" class="pa-0">
          <v-icon class="pa-1" color="warning" medium>warning</v-icon>
          <span>{{ 'WARNING: ' + maxSelectedOverlap.descr }}</span>
        </div>
      </div>
    </v-sheet>

    <v-dialog v-model="colorPickerDialog" persistent width="unset">
      <v-card class="rounded-lg" style="border: 3px solid #3f51b5;">
        <v-card-title color="white" class="ma-0 pa-2" primary-title>
          <span
            v-if="colorPickerApplyToSelected"
            class="primary--text text--darken-3 title"
            >Choose color gradient for {{ selected.length }} selected study
            groups</span
          >
          <span v-else class="primary--text text--darken-3 title"
            >Choose color for study group "{{
              colorPickerCohort ? colorPickerCohort.label : ''
            }}"</span
          >
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="py-4">
          <v-container>
            <v-row>
              <v-col :cols="colorPickerApplyToSelected ? 6 : 12">
                <span v-if="colorPickerApplyToSelected">start color:</span>
                <span v-else>select color:</span>
                <v-color-picker
                  v-model="colorPickerColor"
                  class="pt-2"
                  @update:color="colorChange"
                >
                </v-color-picker>
              </v-col>

              <v-col v-if="colorPickerApplyToSelected" cols="6">
                <span>end color:</span>
                <v-color-picker
                  v-model="colorPickerColor2"
                  class="pt-2"
                  @update:color="colorChange"
                >
                </v-color-picker>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <span>select fill pattern:</span>
                <v-list class="pt-2">
                  <v-list-item-group v-model="colorPickerSelectedPatternInd">
                    <v-list-item
                      v-for="(p, index) in patterns"
                      :key="'sfp-' + index"
                      class="pa-0 ma-0"
                      height="25"
                    >
                      <v-list-item-avatar
                        rounded="0"
                        height="25"
                        class="pa-0 ma-0 ml-2"
                      >
                        <svg width="40" height="25">
                          <g>
                            <rect
                              x="0"
                              y="0"
                              rx="0"
                              ry="0"
                              border-radius="0%"
                              width="40"
                              height="25"
                              :fill="colorPickerColor"
                              stroke="black"
                            />
                            <rect
                              x="0"
                              y="0"
                              rx="0"
                              ry="0"
                              border-radius="0%"
                              width="40"
                              height="25"
                              :fill="'url(#' + p['id'] + ')'"
                              opacity="0.25"
                            />
                          </g>
                        </svg>
                      </v-list-item-avatar>

                      <v-list-item-content class="pa-0 ma-0 ml-2">
                        <v-list-item-title> {{ p.id }} </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
              </v-col>
            </v-row>
          </v-container>

          <v-checkbox
            v-if="selected.length > 1"
            v-model="colorPickerApplyToSelected"
            :label="
              'Apply color gradient to all ' +
                selected.length +
                ' selected study groups'
            "
            class="pa-0 ma-0"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn
            text
            color="red lighten-2"
            @click="closeColorPickerDialog(true)"
          >
            <v-icon left>close</v-icon> Cancel
          </v-btn>

          <v-btn
            class="primary white--text ma-0 px-2 mx-2"
            @click="closeColorPickerDialog(false)"
          >
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { format } from 'd3-format';
import { scaleLinear } from 'd3-scale';
import { color } from 'd3-color';
import { patterns } from '@/utils/patterns';

export default {
  props: {
    title: {
      type: String,
      required: false,
      default: 'Study Groups',
    },
    showTitleBar: {
      type: Boolean,
      required: false,
      default: true,
    },
    cohorts: {
      type: Array,
      required: true,
    },
    // cohorts to select on initial load
    selectCohorts: {
      type: Array,
      required: false,
      default: () => [],
    },
    showSelect: {
      type: Boolean,
      required: false,
      default: false,
    },
    showColors: {
      type: Boolean,
      required: false,
      default: false,
    },
    reportMaxSelectedOverlap: {
      type: Boolean,
      required: false,
      default: false,
    },
    reportMaxOverlap: {
      type: Boolean,
      required: false,
      default: false,
    },
    disablePagination: {
      type: Boolean,
      required: false,
      default: false,
    },
    checkboxTooltip: {
      type: String,
      required: false,
      default: 'Check to select this study group.',
    },
    expanded: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  data() {
    return {
      selected: [],
      expandedVert: true,
      maxOverlap: null,
      maxSelectedOverlap: null,
      colorPickerDialog: false,
      colorPickerCohort: null,
      colorPickerOriginalColorsAndPatterns: null,
      colorPickerColor: null,
      colorPickerColor2: null,
      colorPickerApplyToSelected: false,
      patterns: patterns,
      colorPickerSelectedPatternInd: null,
    };
  },
  computed: {
    headers() {
      var hdrs = [];
      hdrs.push({
        text: 'Name',
        value: 'label',
        class: 'text-subtitle-1 font-weight-bold',
      });

      if (this.showColors) {
        hdrs.push({
          text: 'Color',
          value: 'color',
          class: 'text-subtitle-1 font-weight-bold',
        });
      }

      if (this.expanded) {
        hdrs.push({
          text: 'Size',
          value: 'size',
          class: 'text-subtitle-1 font-weight-bold',
        });

        hdrs.push({
          text: 'Query',
          value: 'query_string',
          class: 'text-subtitle-1 font-weight-bold',
        });
      }

      return hdrs;
    },
    sortedSelectedCohorts() {
      let sel = this.selected;
      let sel_ids = {};
      sel.forEach(c => {
        sel_ids[c['id']] = 1;
      });
      let sel_sorted = [];
      this.cohorts.forEach(c => {
        if (c.id in sel_ids) {
          sel_sorted.push(c);
        }
      });
      return sel_sorted;
    },
  },
  watch: {
    selected(nsel) {
      this.$emit('selectedCohorts', nsel);
      // compute and store maximum overlap between any two _selected_ cohorts
      if (this.reportMaxSelectedOverlap) {
        var max_o = this.computeMaxOverlap(nsel);
        this.maxSelectedOverlap = max_o;
        this.$emit('maxSelectedOverlap', max_o);
      }
    },
    colorPickerSelectedPatternInd() {
      this.colorChange();
    },
    colorPickerApplyToSelected(nv) {
      if (nv) {
        let ssel = this.sortedSelectedCohorts;
        this.colorPickerColor = ssel[0].color;
        this.colorPickerColor2 = ssel[ssel.length - 1].color;
        this.colorPickerSelectedPatternInd = null;
      }
    },
  },
  created() {
    // compute and store maximum overlap between any two cohorts
    if (this.reportMaxOverlap) {
      var max_o = this.computeMaxOverlap(this.cohorts);
      this.maxOverlap = max_o;
      this.$emit('maxOverlap', max_o);
    }
    if (this.selectCohorts) {
      this.selected = this.selectCohorts;
    }
  },
  methods: {
    computeMaxOverlap(cohorts) {
      var overlaps = this.computeOverlaps(cohorts);
      var sortedOverlaps = overlaps.sort((a, b) => b.max_pct - a.max_pct);

      if (overlaps.length > 0) {
        return sortedOverlaps[0];
      } else {
        return null;
      }
    },
    computeOverlaps(cohorts) {
      var overlaps = [];

      // build subject id index for each cohort
      var subjIdsH = [];
      cohorts.forEach(c => {
        var h = {};
        c.subject_ids.forEach(s => {
          h[s] = 1;
        });
        subjIdsH.push(h);
      });

      // perform all vs. all comparison (N^2)
      var nc = cohorts.length;
      for (var i = 0; i < nc; ++i) {
        for (var j = i + 1; j < nc; ++j) {
          // compare i and j
          var n_in_both = 0;
          cohorts[i].subject_ids.forEach(s => {
            if (s in subjIdsH[j]) {
              ++n_in_both;
            }
          });
          if (n_in_both == 0) {
            continue;
          }
          var a_pct = (n_in_both / cohorts[i].subject_ids.length) * 100.0;
          var b_pct = (n_in_both / cohorts[j].subject_ids.length) * 100.0;
          var descr = null;
          var max_pct = null;
          var plural_subject = n_in_both > 1 ? 'subjects' : 'subject';
          var plural_is = n_in_both > 1 ? 'are' : 'is';

          if (a_pct > b_pct) {
            max_pct = a_pct;
            descr =
              n_in_both +
              ' ' +
              plural_subject +
              ' (' +
              format('.1f')(a_pct) +
              "%) from study group '" +
              cohorts[i].label +
              "' " +
              plural_is +
              " also in study group '" +
              cohorts[j].label +
              "'";
          } else {
            max_pct = b_pct;
            descr =
              n_in_both +
              ' ' +
              plural_subject +
              ' (' +
              format('.1f')(b_pct) +
              "%) from study group '" +
              cohorts[j].label +
              "' " +
              plural_is +
              " also in study group '" +
              cohorts[i].label +
              "'";
          }
          overlaps.push({
            a: cohorts[i],
            b: cohorts[j],
            a_pct: a_pct,
            b_pct: b_pct,
            max_pct: max_pct,
            n_in_both: n_in_both,
            descr: descr,
          });
        }
      }
      return overlaps;
    },
    deselectAll() {
      this.selected = [];
    },
    openColorPickerDialog(cohort) {
      this.colorPickerApplyToSelected = false;
      this.colorPickerCohort = cohort;
      this.colorPickerColor = cohort.color;
      this.colorPickerColor2 = cohort.color;
      this.colorPickerSelectedPatternInd = cohort.pattern
        ? cohort.pattern.ind
        : 0;

      // save color assignments for all study groups
      this.colorPickerOriginalColorsAndPatterns = {};
      this.cohorts.forEach(sg => {
        this.colorPickerOriginalColorsAndPatterns[sg.id] = {
          color: sg.color,
          pattern: sg.pattern,
        };
      });
      this.colorPickerDialog = true;
    },
    closeColorPickerDialog(cancel) {
      if (cancel) {
        // restore original colors/patterns
        this.cohorts.forEach(sg => {
         if (
            sg.color !=
              this.colorPickerOriginalColorsAndPatterns[sg.id]['color'] ||
            (sg.pattern &&
              sg.pattern.ind !=
                this.colorPickerOriginalColorsAndPatterns[sg.id]['pattern'][
                  'ind'
                ])
          ) {
            this.$emit('cohortColorChange', {
              cohort: sg,
              color: this.colorPickerOriginalColorsAndPatterns[sg.id]['color'],
              pattern: this.colorPickerOriginalColorsAndPatterns[sg.id][
                'pattern'
              ],
            });
          }
        });
      }
      this.colorPickerDialog = false;
    },
    colorChange() {
      // multiple study group change
      if (this.colorPickerApplyToSelected) {
        // apply consecutive patterns in the order the cohorts appear in the original list
        let ssel = this.sortedSelectedCohorts;
        let n_cohorts = ssel.length;
        let n_patterns = this.patterns.length;
        let colorGrad = scaleLinear()
          .domain([1, n_cohorts])
          .range([this.colorPickerColor, this.colorPickerColor2]);

        for (let g = 0; g < n_cohorts; ++g) {
          let col = color(colorGrad(g + 1)).formatHex();
          let cevt = {
            cohort: ssel[g],
            color: col,
          };
          if (this.colorPickerSelectedPatternInd != null) {
            cevt['pattern'] = this.patterns[
              (this.colorPickerSelectedPatternInd + g) % n_patterns
            ];
          }
          this.$emit('cohortColorChange', cevt);
        }
      }
      // single study group change
      else {
        this.$emit('cohortColorChange', {
          cohort: this.colorPickerCohort,
          color: this.colorPickerColor,
          pattern:
            this.colorPickerSelectedPatternInd != null
              ? this.patterns[this.colorPickerSelectedPatternInd]
              : null,
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
tr.selectedRow {
  background-color: rgb(236, 177, 212);
}
tbody {
  tr:hover {
    background-color: transparent !important;
  }
}

.v-list {
  height: 200px;
  overflow-y: auto;
}
</style>
