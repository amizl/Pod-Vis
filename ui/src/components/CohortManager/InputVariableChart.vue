<template>
  <ColumnChart
    v-if="variable.type === 'subject'"
    :id="variable.id"
    :label="variable.label"
  />
  <div v-else></div>
</template>

<script>
import ColumnChart from '@/components/CohortManager/ColumnChart.vue';

export default {
  components: {
    ColumnChart,
  },
  props: {
    variable: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped></style>
