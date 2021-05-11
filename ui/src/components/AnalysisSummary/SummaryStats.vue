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
                [
                  { abbreviation: 'Predictors' },
                  ...predictorVariables,
                  { abbreviation: 'Outcomes' },
                  ...outcomeVariables,
                ].filter(v => v.data_category != 'Categorical')
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
                    <th v-for="c in cohorts" :key="c.id" colspan="3">
                      <v-chip x-small :color="c.color" class="my-1 px-2" />
                      <span class="subtitle-1 pl-2 font-weight-bold">{{
                        c.label
                      }}</span>
                    </th>
                  </tr>
                </thead>
              </template>

              <template v-slot:item="v">
                <tr>
                  <td>
                    <span :class="getNameClass(v.item.abbreviation)">{{
                      getVariableName(v.item)
                    }}</span>
                  </td>
                  <template v-for="c in cohorts">
                    <td :key="'cmean-' + c.id">{{ cohortMean(v.item, c) }}</td>
                    <td :key="'cmedian-' + c.id">
                      {{ cohortMedian(v.item, c) }}
                    </td>
                    <td :key="'cdev-' + c.id">
                      {{ cohortDeviation(v.item, c) }}
                    </td>
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
import { mean, median, deviation } from 'd3-array';
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
    isLongitudinal: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  data() {
    return {
      colors: colors,
      cohortStats: {},
      dimension2field: {
        left_y_axis: 'firstVisit',
        right_y_axis: 'lastVisit',
        change: 'change',
        roc: 'roc',
      },
      var2visits: {},
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
      this.cohorts.forEach(() => {
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
    collection(new_collection) {
      this.updateVisits(new_collection);
    },
    outcomeVariables() {
      this.updateCohortStats();
    },
    data() {
      this.updateCohortStats();
    },
  },
  mounted() {
    this.updateVisits(this.collection);
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
              // outcome variable dimension used as input variable
              if ('dimension_label' in pv) {
                var ont_id = pv.observation_ontology.id;
                var key = ont_id + ':' + pv.dimension_label;
                if (!(key in cohortData[c.id])) cohortData[c.id][key] = [];
                cohortData[c.id][key].push(
                  d[ont_id][this.dimension2field[pv.dimension_label]]
                );
              }
              // subject variable used as input variable
              else if (
                !('observation_ontology' in pv) ||
                pv.observation_ontology == null
              ) {
                var oo_id = pv.id;
                if (!(oo_id in cohortData[c.id])) cohortData[c.id][oo_id] = [];
                cohortData[c.id][oo_id].push(d[pv.label]);
              }
            });

            var cfield = this.is_longitudinal ? this.comparisonField : 'value';
            this.outcomeVariables.forEach(ov => {
              if (!(ov.id in cohortData[c.id])) cohortData[c.id][ov.id] = [];
              cohortData[c.id][ov.id].push(d[ov.id][cfield]);
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
          var key =
            'dimension_label' in ov
              ? ov.observation_ontology.id + ':' + ov.dimension_label
              : ov.id;
          this.cohortStats[c.id][key] = {};
          var cdata = cohortData[c.id][key];
          this.cohortStats[c.id][key]['mean'] = format('.1~f')(mean(cdata));
          this.cohortStats[c.id][key]['median'] = format('.1~f')(median(cdata));
          this.cohortStats[c.id][key]['deviation'] = format('.1~f')(
            deviation(cdata)
          );
        });
      });
    },
    cohortStat(v, c, stat) {
      if (v.abbreviation == 'Predictors' || v.abbreviation == 'Outcomes') {
        return '';
      }
      if (c.id in this.cohortStats) {
        var cs = this.cohortStats[c.id];
        if (v.id in cs) {
          return cs[v.id][stat];
        } else if ('dimension_label' in v) {
          var key = v.observation_ontology.id + ':' + v['dimension_label'];
          return cs[key][stat];
        }
      }
      return '-';
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
      var cls = 'subtitle-1 font-weight-bold';
      if (n != 'Predictors' && n != 'Outcomes') {
        cls = cls + ' pl-3';
      }
      return cls;
    },
    updateVisits(collection) {
      // build mapping from observation input variable to visit names
      this.var2visits = {};

      collection.observation_variables_list.forEach(ov => {
        var ov_id = ov.ontology.id;
        this.var2visits[ov_id] = {};

        if (ov['first_visit_event']) {
          this.var2visits[ov_id]['firstVisit'] = ov['first_visit_event'];
          this.var2visits[ov_id]['lastVisit'] = ov['last_visit_event'];
        } else {
          this.var2visits[ov_id]['firstVisit'] = ov['first_visit_num'];
          this.var2visits[ov_id]['lastVisit'] = ov['last_visit_num'];
        }
      });
    },
    getVariableName(v) {
      if ('abbreviation' in v) return v.abbreviation;
      var field = this.dimension2field[v.dimension_label];
      var vv = this.var2visits[v.observation_ontology.id];
      if (vv == null)
        return v.observation_ontology.abbreviation + ' - ' + field;
      if (field in vv) {
        field = this.var2visits[v.observation_ontology.id][field];
      }
      return v.observation_ontology.abbreviation + ' - ' + field;
    },
  },
};
</script>

<style lang="scss" scoped></style>
