<template>
  <v-sheet color="white" class="rounded-lg shadow">
    <v-container v-if="showTitleBar" fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-container fluid fill-width class="ma-0 pa-0">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-card color="#eeeeee" class="pt-1">
                  <v-card-title class="primary--text pl-3 py-2"
                    >Cohort Statistics
                  </v-card-title>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-container>

    <v-sheet color="white" class="my-3 rounded-lg shadow">
      <v-container fluid fill-width class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-data-table
              :headers="headers"
              :items="
                [{ 'abbreviation': 'Predictors' }, ...predictorVariables, { 'abbreviation': 'Outcomes' }, ...outcomeVariables].filter(
                  v => v.data_category != 'Categorical'
                )
              "
              item-key="id"
              :disable-pagination="true"
              :hide-default-footer="true"
              dense
            >
              <template v-slot:header="props">
                <thead>
                  <tr>
                    <th colspan="1"></th>
                    <th v-for="c in cohorts" colspan="3">
                      <v-chip x-small :color="c.color" class="my-1 px-2" />
                      <span class="subtitle-1 pl-2 font-weight-bold">{{ c.label }}</span>
                    </th>
                  </tr>
                </thead>
              </template>

              <template v-slot:item="v">
                <tr>
                  <td>
                    <span :class="getNameClass(v.item.abbreviation)">{{ v.item.abbreviation }}</span>
                  </td>
                  <template v-for="c in cohorts">
                    <td>{{ cohortMean(v.item, c) }}</td>
                    <td>{{ cohortMedian(v.item, c) }}</td>
                    <td>{{ cohortDeviation(v.item, c) }}</td>
                  </template>
                </tr>
              </template>
            </v-data-table>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state as deState } from '@/store/modules/dataExplorer/types';
import { min, max, mean, median, deviation } from 'd3-array';
import { format } from 'd3-format';
import { colors } from '@/utils/colors';
import 'd3-transition';

export default {
  components: {},
  props: {
    showTitleBar: {
      type: Boolean,
      required: false,
      default: true,
    },
    cohorts: {
      type: Array,
      required: true,
      default: () => [],
    },
    predictorVariables: {
      type: Array,
      required: true,
      default: () => [],
    },
    outcomeVariables: {
      type: Array,
      required: true,
      default: () => [],
    },
    comparisonField: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      colors: colors,
      cohortStats: {},
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      collection: deState.COLLECTION,
      data: deState.DATA,
    }),
    headers() {
      var hdrs = [];
      hdrs.push({
        text: 'Variable',
        value: 'abbreviation',
        sortable: false,
      });
      this.cohorts.forEach(c => {
        hdrs.push({
          text: 'Mean',
          value: 'mean',
          sortable: false,
        });
        hdrs.push({
          text: 'Median',
          value: 'median',
          sortable: false,
        });
        hdrs.push({
          text: 'Deviation',
          value: 'deviation',
          sortable: false,
        });
      });

      return hdrs;
    },
  },
  watch: {
    cohorts() {
      this.updateCohortStats();
    },
    outcomeVariables() {
      this.updateCohortStats();
    },
    data() {
      this.updateCohortStats();
    },
  },
  mounted() {
    this.updateCohortStats();
  },
  methods: {
    updateCohortStats() {
      if (
        this.cohorts == null ||
        this.outcomeVariables == null ||
        this.data == null
      )
        return;

      // index cohort subjects
      var cohortSubjs = {};
      this.cohorts.forEach(c => {
        cohortSubjs[c.id] = {};
        var subjIds = c.subject_ids;
        //        console.log("cohort " + c.label + " has " + subjIds.length + " subject(s)");
        subjIds.forEach(sid => {
          cohortSubjs[c.id][sid] = 1;
        });
      });

      // sort data by cohort and variable
      var cohortData = {};
      this.data.forEach(d => {
        var subjId = d.subject_id;
        this.cohorts.forEach(c => {
          if (subjId in cohortSubjs[c.id]) {
            if (!(c.id in cohortData)) cohortData[c.id] = {};

            this.predictorVariables.forEach(pv => {
              if (
                !('observation_ontology' in pv) ||
                pv.observation_ontology == null
              ) {
                var ont_id = pv.id;
                if (!(ont_id in cohortData[c.id]))
                  cohortData[c.id][ont_id] = [];
                cohortData[c.id][ont_id].push(d[pv.label]);
              } else {
                if (!(pv.id in cohortData[c.id])) cohortData[c.id][pv.id] = [];
                cohortData[c.id][pv.id].push(d[pv.id][this.comparisonField]);
              }
            });

            this.outcomeVariables.forEach(ov => {
              if (!(ov.id in cohortData[c.id])) cohortData[c.id][ov.id] = [];
              cohortData[c.id][ov.id].push(d[ov.id][this.comparisonField]);
            });
          }
        });
      });

      this.cohorts.forEach(c => {
        this.cohortStats[c.id] = {};
        const allVars = [
          ...this.predictorVariables,
          ...this.outcomeVariables,
        ].filter(v => v.data_category != 'Categorical');
        allVars.forEach(ov => {
          this.cohortStats[c.id][ov.id] = {};
          var cdata = cohortData[c.id][ov.id];
          //          console.log("c=" + c.label + " v=" + ov.label + " visit=" + this.comparisonField + " data=" + cdata);
          this.cohortStats[c.id][ov.id]['mean'] = format('.1~f')(mean(cdata));
          this.cohortStats[c.id][ov.id]['median'] = format('.1~f')(
            median(cdata)
          );
          this.cohortStats[c.id][ov.id]['deviation'] = format('.1~f')(
            deviation(cdata)
          );
        });
      });
    },
    cohortStat(v, c, stat) {
      if (v.abbreviation == 'Predictors' || v.abbreviation == 'Outcomes') {
        return '';
      }
      if (!(c.id in this.cohortStats) || !(v.id in this.cohortStats[c.id])) {
        return '-';
      }
      return this.cohortStats[c.id][v.id][stat];
    },
    cohortMean(v, c) {
      return this.cohortStat(v, c, 'mean');
    },
    cohortMedian(v, c) {
      return this.cohortStat(v, c, 'median');
    },
    cohortDeviation(v, c) {
      return this.cohortStat(v, c, 'deviation');
    },
    getNameClass(n) {
      var cls = "subtitle-1 font-weight-bold";
      if ((n != 'Predictors') && (n != 'Outcomes')) {
        cls = cls + " pl-3"
      }
      return cls;
   },
},
};
</script>

<style lang="scss" scoped></style>
