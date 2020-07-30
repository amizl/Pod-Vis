<template>
  <div>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              >{{ title }}
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-sheet color="white" class="rounded-lg shadow">

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

      <template v-slot:item.overlaps="{ item }">
        <td class="subtitle-1 text-xs-left">{{ item.overlaps }}</td>
      </template>
    </v-data-table>

    <div class="ma-0 pa-3" style="height: 3em" v-if="reportMaxOverlap">
      <div v-if="maxSelectedOverlap" class="pa-0">
	<v-icon class="pa-1" color="error" medium>warning</v-icon>
	<span>{{ "WARNING: " + maxSelectedOverlap.descr }}</span>
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
    showSelect: {
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
      maxOverlap: null,
      maxSelectedOverlap: null,
    };
  },
  computed: {
    headers() {
      var hdrs = [
        {
          text: 'Cohort Name',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Cohort Size',
          value: 'size',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Query',
          value: 'query_string',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ];
      if (this.showSelect) {
        hdrs.push({
          text: 'Overlaps',
          value: 'overlaps',
          class: 'text-subtitle-1 font-weight-bold',
        });
      }
      return hdrs;
    },
  },
  created() {
      if (this.reportMaxOverlap) {
        var max_o = this.computeMaxOverlap(this.cohorts);
        this.maxOverlap = max_o;
        this.$emit('maxOverlap', max_o);
      }
  },
  watch: {
    cohorts(cohorts) {
console.log("cohorts changed");
    },
    selected(nsel) {
      this.$emit('selectedCohorts', nsel);
      if (this.reportMaxOverlap) {
        var max_o = this.computeMaxOverlap(nsel);
        this.maxSelectedOverlap = max_o;
        this.$emit('maxSelectedOverlap', max_o);
      }
    },
  },
  methods: {
    computeMaxOverlap(cohorts) {
      var overlaps = this.computeOverlaps(cohorts);
      var sortedOverlaps = overlaps.sort((a,b) => b.max_pct - a.max_pct);

      if (overlaps.length > 0) {
        return sortedOverlaps[0];
      } else {
        return null;
      }
    },
    computeOverlaps(cohorts) {
      var overlaps = [];

      var subjIdsH = [];
      cohorts.forEach(c => {
        var h = {};
        c.subject_ids.forEach(s => {
          h[s] = 1;
        });
        subjIdsH.push(h);
      });

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
			  if (n_in_both == 0) { continue; }
	  var a_pct = (n_in_both / cohorts[i].subject_ids.length) * 100.0;
	  var b_pct = (n_in_both / cohorts[j].subject_ids.length) * 100.0;
          var descr = null;
	  var max_pct = null;

			  if (a_pct > b_pct) {
max_pct = a_pct;
descr = format('.2f')(a_pct) + "% of cohort '" + cohorts[i].label + "' is contained in cohort '" + cohorts[j].label + "'";
} else {
max_pct = b_pct;
descr = format('.2f')(b_pct) + "% of cohort '" + cohorts[j].label + "' is contained in cohort '" + cohorts[i].label + "'";
}
			  overlaps.push({
			  'a': cohorts[i],
'b': cohorts[j],
'a_pct': a_pct,
'b_pct': b_pct,
'max_pct': max_pct,
			  'n_in_both': n_in_both,
			  'descr': descr,
			});
	}
      }
return overlaps;
},
  },
};
</script>

<style></style>
