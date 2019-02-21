<template lang="pug">
  v-container(fluid)
    v-toolbar(app flat)
      p.subheading.foo--text.ml-5.mt-5 Create cohort for Parkinson's Disease
      v-spacer
      v-btn Foo
    v-layout(align-center justify-start row fill-height)
      v-flex(xs12)
        v-card.ui-card
          parallel-coordinates

</template>

<script>
import { mapState, mapActions } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';
import CohortCard from '@/components/CohortManager/CohortCard.vue';
import ParallelCoordinates from '@/components/charts/ParallelCoordinates.vue';
import ContentHeader from '../components/layout/Header.vue';

export default {
  components: {
    CohortCard,
    ContentHeader,
    ParallelCoordinates,
  },
  computed: {
    ...mapState('cohortManager', {
      cohorts: state.COHORTS,
    }),
  },
  created() {
    this.fetchCohorts();
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCohorts: actions.FETCH_COHORTS,
    }),
  },
};
</script>

<style scoped></style>
