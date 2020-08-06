<template>
  <v-container fill-width class="pa-0 ma-0">
    <!-- ParallelCoordinates plot - requires first + last visit selected -->
    <v-row
      v-if="
        variable.data_category !== 'Categorical' &&
          (!variable.selected_measures ||
            ('firstVisit' in variable.selected_measures &&
              'lastVisit' in variable.selected_measures))
      "
      class="pa-2 ma-0"
    >
      <v-col cols="12" class="pa-0 ma-0">
        <ParallelCoordinates
          :dimension-name="dimensionName"
          :variable="variable"
          :first-visit-label="firstVisitLabel"
          :last-visit-label="lastVisitLabel"
          @userChangedVariable="userChangedVariable"
        />
      </v-col>
    </v-row>

    <!-- Individual plots for first and last visit -->
    <v-row v-else class="pa-0 ma-0">
      <v-col cols="12" class="pa-0 ma-0">
        <v-container fill-width class="pa-0 ma-0">
          <v-row
            v-if="'firstVisit' in variable.selected_measures"
            class="not-highlight-var pa-2 ma-0"
          >
            <v-col cols="12" class="pa-0 ma-0">
              First Visit: {{ firstVisitLabel }}
              <HistogramChart
                v-if="variable.data_category !== 'Categorical'"
                :id="`firstVisit-${dimensionName}`"
                class="ma-1"
                :dimension-name="`${variable.label} - First Visit`"
                :variable="variable"
                @userChangedVariable="userChangedVariable"
              />
              <ColumnChart
                v-else
                :id="variable.id"
                :dimension-name="`${variable.label} - First Visit`"
                @userChangedVariable="userChangedVariable"
              />
            </v-col>
          </v-row>
          <v-row
            v-if="'lastVisit' in variable.selected_measures"
            class="not-highlight-var pa-2 ma-0"
          >
            <v-col cols="12" class="pa-0 ma-0">
              Last Visit: {{ lastVisitLabel }}
              <HistogramChart
                v-if="variable.data_category !== 'Categorical'"
                :id="`lastVisit-${dimensionName}`"
                class="ma-1"
                :dimension-name="`${variable.label} - Last Visit`"
                :variable="variable"
                @userChangedVariable="userChangedVariable"
              />
              <ColumnChart
                v-else
                :id="variable.id"
                :dimension-name="`${variable.label} - Last Visit`"
                @userChangedVariable="userChangedVariable"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>

    <!-- Individual plots for Change, Rate of Change -->

    <v-row
      v-if="
        variable.data_category !== 'Categorical' &&
          (!variable.selected_measures ||
            'change' in variable.selected_measures)
      "
      class="pa-2 ma-0"
      :class="highlightChange ? 'highlight-var' : 'not-highlight-var'"
    >
      <v-col cols="12" class="pa-0 ma-0">
        Change: {{ firstVisitLabel }}-{{ lastVisitLabel }}
        <HistogramChart
          :id="`change-${dimensionName}`"
          :dimension-name="`${variable.label} - Change`"
          :variable="variable"
          @userChangedVariable="userChangedVariable"
        />
      </v-col>
    </v-row>

    <v-row
      v-if="
        variable.data_category !== 'Categorical' &&
          (!variable.selected_measures || 'roc' in variable.selected_measures)
      "
      class="pa-2 ma-0"
      :class="'not-highlight-var'"
    >
      <v-col cols="12" class="pa-0 ma-0">
        Rate of Change: {{ firstVisitLabel }}-{{ lastVisitLabel }}
        <HistogramChart
          :id="`roc-${dimensionName}`"
          :dimension-name="`${variable.label} - Rate of Change`"
          :variable="variable"
          @userChangedVariable="userChangedVariable"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ParallelCoordinates from '@/components/CohortManager/ParallelCoordinates.vue';
import ColumnChart from '@/components/CohortManager/BarChart/BarChart.vue';
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';

export default {
  components: {
    ColumnChart,
    ParallelCoordinates,
    HistogramChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
    dimensionName: {
      type: Number,
      required: true,
    },
    highlightChange: {
      type: Boolean,
      required: false,
    },
    firstVisitLabel: {
      type: String,
      required: false,
      default: 'First Visit',
    },
    lastVisitLabel: {
      type: String,
      required: false,
      default: 'Last Visit',
    },
  },
  methods: {
    userChangedVariable() {
      this.$emit('userChangedVariable');
    },
  },
};
</script>

<style lang="scss" scoped></style>
