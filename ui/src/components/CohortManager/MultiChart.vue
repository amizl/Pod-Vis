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
            <v-flex>First Visit</v-flex>
            <v-flex pl-5 ml-5>Last Visit</v-flex>
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
            xs6
            class="pb-0"
          >
            First Visit
            <HistogramChart
              :id="`firstVisit-${dimensionName}`"
              class="ma-1"
              :dimension-name="`${variable.label} - First Visit`"
            />
          </v-flex>
          <v-flex
            v-if="'lastVisit' in variable.selected_measures"
            xs6
            class="pb-0"
          >
            Last Visit
            <HistogramChart
              :id="`lastVisit-${dimensionName}`"
              class="ma-1"
              :dimension-name="`${variable.label} - Last Visit`"
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
            xs6
            class="pb-0"
          >
            Change
            <HistogramChart
              :id="`change-${dimensionName}`"
              :dimension-name="`${variable.label} - Change`"
            />
          </v-flex>
          <v-flex
            v-if="
              !variable.selected_measures || 'roc' in variable.selected_measures
            "
            xs6
            class="pt-0"
          >
            Rate of Change
            <HistogramChart
              :id="`change-${dimensionName}`"
              :dimension-name="`${variable.label} - Rate of Change`"
            />
          </v-flex>
        </v-layout>
      </v-flex>
      <!-- <v-flex xs2> </v-flex> -->
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
  },
};
</script>

<style lang="scss" scoped></style>
