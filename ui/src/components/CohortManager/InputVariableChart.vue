<template>
  <v-sheet color="white" height="100%" min-width="300px" max-width="500px">
    <v-layout column fill-height>
      <v-card-title
        class="subtitle-1 primary--text text--darken-4 pa-0 ma-0 text-truncate"
      >
        <v-layout
          align-center
          style="background-color: white; padding: 0.5em 0em 1em 0.4em; border-radius: 0.5rem;"
        >
          <span style="padding: 0.4em 0.5em 1em 0.5em">
            <img
              v-if="variable.label !== 'Dataset'"
              :src="'/images/' + variable.category + '-icon-128.png'"
              :title="variable.category"
              style="height:3em"
            />
            <img
              v-else
              src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs%3D"
              width="0"
              style="height: 3em"
              alt=""
            />
          </span>
          {{ getChartTitle() }}
          <v-spacer />
          <v-btn
            flat
            class="subheading primary--text text--lighten-4"
            @click="clearFilter({ dimension })"
          >
            Reset
          </v-btn>
        </v-layout>
      </v-card-title>

      <v-layout fill-height>
        <div v-if="variable.value_type === 'date'" class="pl-3 pt-3">
          Date types not supported.
        </div>
        <ColumnChart
          v-else-if="
            (!variable.is_longitudinal &&
              variable.data_category === 'Categorical') ||
              variable.type === 'study'
          "
          :id="variable.id"
          :dimension-name="dimension"
          bar-tooltip="Click to add or remove this value from the cohort filter"
        />
        <HistogramChart
          v-else
          :id="variable.id"
          :dimension-name="dimension"
          :variable="variable"
          input-variable
        />
      </v-layout>
    </v-layout>
  </v-sheet>
</template>

<script>
import ColumnChart from '@/components/CohortManager/BarChart/BarChart.vue';
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';

export default {
  components: {
    ColumnChart,
    HistogramChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
  },
  data() {
    return { dimension: null };
  },
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      unfilteredData: state.UNFILTERED_DATA,
    }),
  },
  created() {
    this.addDimensionHelper(this.variable);
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
      clearFilter: actions.CLEAR_FILTER,
    }),
    getChartTitle() {
      var title = this.variable.label;
      if (
        this.variable.type == 'observation' &&
        this.variable.is_longitudinal
      ) {
        var visit = this.variable.label;
        //     var which = this.variable.label == 'First Visit' ? 'first' : 'last';
        var fv = null;
        var lv = null;

        this.collection.observation_variables_list.forEach(ov => {
          if (ov.ontology.id == this.variable.parentID) {
            if (ov['first_visit_event']) {
              fv = ov['first_visit_event'];
              lv = ov['last_visit_event'];
            } else {
              fv = ov['first_visit_num'];
              lv = ov['last_visit_num'];
            }
          }
        });
        if (this.variable.label == 'First Visit') {
          title = this.variable.parentLabel + ' - ' + fv;
        } else if (this.variable.label == 'Last Visit') {
          title = this.variable.parentLabel + ' - ' + lv;
        } else {
          title =
            this.variable.parentLabel +
            ' - ' +
            this.variable.label +
            ': ' +
            fv +
            '-' +
            lv;
        }
      }
      return title;
    },
    addDimensionHelper(variable) {
      var dimensionName = null;
      var payload = null;

      // observation variable
      if (this.variable.type === 'observation') {
        var dimensionId = null;
        var measure = null;

        if (variable.is_longitudinal) {
          measure = this.variable.id.split('-')[0];
          dimensionName = `${this.variable.parentLabel} - ${
            this.variable.label
          }`;
          dimensionId = this.variable.parentID;
        } else {
          measure = 'value';
          dimensionName = variable.label;
          dimensionId = variable.id;
        }
        payload = {
          dimensionName,
          accessor: d => {
            const dimName = dimensionId;
            return d[dimName][measure];
          },
        };
      }
      // subject variable
      else {
        if (
          this.variable.label === 'Study' ||
          this.variable.label === 'Dataset'
        ) {
          dimensionName = this.variable.label;
          payload = {
            dimensionName: dimensionName,
            accessor: d => d.study.study_name,
          };
        } else {
          dimensionName = this.variable.label;
          payload = {
            dimensionName: dimensionName,
            accessor: d => {
              const dimName = dimensionName;
              return d[dimName];
            },
          };
        }
      }
      this.dimension = dimensionName;
      this.addDimension(payload);
    },
  },
};
</script>

<style lang="scss" scoped></style>
