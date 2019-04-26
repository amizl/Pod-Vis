<template lang="pug">
  v-card
    //- v-card-title(primary-title) FOO
    v-card-text
      p.subheading DATASETS
      v-chip {{ dataset }}
    v-card-text
      p.subheading OUTCOME MEASURES
      v-chip(v-for='{ name } in outcomeMeasures') {{ name }}
    v-card-text
      // Example filters
      p.subheading FILTERS
      v-chip Male
      v-chip Age > 45

    v-card-actions
      v-spacer
      v-btn(flat) Explore
      v-btn(flat) Analyze
      v-btn(flat) Create
</template>

<script>
export default {
  props: ['dataset', 'outcomeMeasures'],
};
</script>

<style scoped>

</style>
