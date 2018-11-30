<template lang='pug'>
  v-container(fluid)
    v-toolbar(app dense).primary
    v-layout(v-if='cohorts' align-center justify-start row fill-height)
      v-flex(v-for='cohort in cohorts' v-key='cohort.code' md3).pa-3
        cohort-card(
          :dataset='cohort.dataset'
          :outcomeMeasures='cohort.variables'
        )
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';
import CohortCard from '@/components/CohortManager/CohortCard.vue';
import ContentHeader from '../components/layout/Header.vue';

export default {
  components: {
    CohortCard,
    ContentHeader,
  },
  computed: {
    ...mapState('cohortManager', {
      cohorts: state.COHORTS,
    }),
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCohorts: actions.FETCH_COHORTS,
    }),
  },
  created() {
    this.fetchCohorts();
  },
};
</script>

<style scoped>
</style>
