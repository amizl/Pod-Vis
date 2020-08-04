<template>
  <div>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              >{{ title }}
              <v-spacer />
              <v-toolbar-items>
                <v-icon v-if="expanded" @click="expanded = false"
                  >expand_less</v-icon
                >
                <v-icon v-else @click="expanded = true">expand_more</v-icon>
              </v-toolbar-items>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-sheet v-show="expanded" color="white" class="rounded-lg shadow">
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
                No cohorts selected.
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
        dense
      >
        <template v-slot:item.label="{ item }">
          <td class="subtitle-1 text-xs-left">{{ item.label }}</td>
        </template>

        <template v-slot:item.size="{ item }">
          <td class="subtitle-1 text-xs-left">{{ item.subject_ids.length }}</td>
        </template>

        <template v-slot:item.query_string="{ item }">
          <td class="subtitle-1 text-xs-left">{{ item.query_string }}</td>
        </template>

        <template v-slot:item.color="{ item }">
          <v-chip small :color="item.color" class="my-1" />
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
  </div>
</template>

<script>
import { format } from 'd3-format';

export default {
  props: {
    title: {
      type: String,
      required: false,
      default: 'Cohorts',
    },
    cohorts: {
      type: Array,
      required: true,
    },
    // cohorts to select on initial load
    selectCohorts: {
      type: Array,
      required: false,
      default: x => [],
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
  },
  data() {
    return {
      selected: [],
      expanded: true,
      maxOverlap: null,
      maxSelectedOverlap: null,
    };
  },
  computed: {
    headers() {
      var hdrs = [];
      hdrs.push({
        text: 'Cohort Name',
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

      hdrs.push({
        text: 'Cohort Size',
        value: 'size',
        class: 'text-subtitle-1 font-weight-bold',
      });

      hdrs.push({
        text: 'Query',
        value: 'query_string',
        class: 'text-subtitle-1 font-weight-bold',
      });

      return hdrs;
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
              "%) from cohort '" +
              cohorts[i].label +
              "' " +
              plural_is +
              " also in cohort '" +
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
              "%) from cohort '" +
              cohorts[j].label +
              "' " +
              plural_is +
              " also in cohort '" +
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
</style>
