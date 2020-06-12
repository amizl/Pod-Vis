<template>
  <v-flex fill-height>
    <v-layout column fill-height>
      <v-flex xs4>
        <v-flex
          v-if="
            !variable.selected_measures ||
              ('firstVisit' in variable.selected_measures &&
                'lastVisit' in variable.selected_measures)
          "
        >
          <v-layout>
            <v-flex>Visit:{{ firstVisitLabel }}</v-flex>
            <v-flex pl-5 ml-5>Visit:{{ lastVisitLabel }}</v-flex>
          </v-layout>
          <v-layout fill-height>
            <ParallelCoordinates
              :dimension-name="dimensionName"
              :variable="variable"
            />
          </v-layout>
        </v-flex>
        <v-layout v-else>
          <v-flex
            v-if="'firstVisit' in variable.selected_measures"
	    class="not-highlight-var pb-0""
            xs6
          >First Visit: {{ firstVisitLabel }}
            <HistogramChart
              :id="`firstVisit-${dimensionName}`"
              class="ma-1"
              :dimension-name="`${variable.label} - First Visit`"
              :variable="variable"
            />
          </v-flex>
          <v-flex
            v-if="'lastVisit' in variable.selected_measures"
	    class="not-highlight-var pb-0""
            xs6
          >Last Visit: {{ lastVisitLabel }}
            <HistogramChart
              :id="`lastVisit-${dimensionName}`"
              class="ma-1"
              :dimension-name="`${variable.label} - Last Visit`"
              :variable="variable"
            />
          </v-flex>
        </v-layout>
      </v-flex>
      <v-flex xs8>
        <v-layout column fill-height>
          <v-flex
            v-if="
              !variable.selected_measures ||
                'change' in variable.selected_measures
            "
            :class="highlightChange ? 'highlight-var' : 'not-highlight-var'"
            xs6
          >Change: {{ firstVisitLabel }}-{{ lastVisitLabel }}
            <HistogramChart
              :id="`change-${dimensionName}`"
              :dimension-name="`${variable.label} - Change`"
              :variable="variable"
            />
          </v-flex>
          <v-flex
            v-if="
              !variable.selected_measures || 'roc' in variable.selected_measures
              "
	    :class="'not-highlight-var'"
            xs6
          >Rate of Change: {{ firstVisitLabel }}-{{ lastVisitLabel }}
            <HistogramChart
              :id="`roc-${dimensionName}`"
              :dimension-name="`${variable.label} - Rate of Change`"
              :variable="variable"
            />
          </v-flex>
        </v-layout>
     </v-flex>
    </v-layout>
  </v-flex>
</template>

<script>
import ParallelCoordinates from '@/components/CohortManager/ParallelCoordinates.vue';
import HistogramChart from '@/components/CohortManager/HistogramChart/HistogramChart.vue';

export default {
  components: {
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
default: "First Visit"
    },
    lastVisitLabel: {
      type: String,
required: false,
default: "Last Visit"
    },

  },
};
</script>

<style lang="scss" scoped></style>
