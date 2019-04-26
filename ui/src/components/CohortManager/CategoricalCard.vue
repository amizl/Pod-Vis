<template lang="pug">
  v-card(width=500)
    v-card-title(primary-title).primary
      div
        h3.white--text {{ label }}
        div.white--text UPDRS 1
    //-  stacked-bar-chart(:data='data').pt-3
</template>

<script>
// import StackedBarChart from '@/components/charts/StackedBarChart.vue';

export default {
  components: {
    // StackedBarChart,
  },
  props: {
    measure: String,
    label: String,
    data: Array,
  },
  filters: {
    toUpperCase(value) {
      return value.toUpperCase();
    },
  },
};
</script>

<style scoped>

</style>
