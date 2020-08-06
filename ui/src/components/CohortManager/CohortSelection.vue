<template>
  <v-select
    v-model="selectedCohort"
    flat
    dark
    :items="collection_cohorts"
    item-text="label"
    item-value="id"
    return-object
    label="Cohorts"
    solo-inverted
  ></v-select>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';

export default {
  data() {
    return {
      selectedCohort: { id: null },
    };
  },
  computed: {
    ...mapState('cohortManager', {
      cohorts: state.COHORTS,
      cohort: state.COHORT,
      collection: state.COLLECTION,
    }),

    // cohorts are collection-specific
    collection_cohorts() {
      // include a default select that serves as the new cohort option
      const cch = [
        { id: null, label: 'Choose Cohort' },
        { id: -1, label: 'New Cohort' },
      ];
      const cid = this.collection.id;

      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          cch.push(e);
        }
      });

      return cch;
    },
  },
  watch: {
    selectedCohort(newCohort) {
      if (newCohort != this.cohort) {
        this.$emit('selectedCohort', newCohort);
      }
    },
    cohort(nc) {
      if (this.selectedCohort != nc) {
        this.selectedCohort = nc;
      }
    },
  },
  created() {
    this.fetchCohorts();
    if (this.selectedCohort != this.cohort) {
      this.selectedCohort = this.cohort;
    }
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCohorts: actions.FETCH_COHORTS,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
