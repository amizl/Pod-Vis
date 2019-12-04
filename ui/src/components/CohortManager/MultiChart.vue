<template>
  <v-flex fill-height>
    <v-layout column fill-height>
      <v-flex xs4>
        <v-layout fill-height>
          <ParallelCoordinates
            :dimension-name="dimensionName"
            :variable="variable"
          />
        </v-layout>
      </v-flex>
      <v-flex xs8>
        <v-layout column fill-height>
          <v-flex xs6 class="pb-0">
            Change
            <HistogramChart
              :id="`change-${dimensionName}`"
              :dimension-name="`${variable.label} - Change`"
            />
          </v-flex>
          <v-flex xs6 class="pt-0">
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
