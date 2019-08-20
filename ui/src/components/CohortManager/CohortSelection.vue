<template>
  <v-select
    v-model="selectedCohort"
    flat
    dark
    :items="cohorts"
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
      _cohorts: state.COHORTS,
      cohort: state.COHORT,
      collection: state.COLLECTION
    }),
    cohorts() {
      // include a default select that serves as the new cohort option
      var new_ch =  [{ id: null, label: 'New Cohort' }]
      var ch = this._cohorts;
      var cid = this.collection.id;

      // cohorts are collection-specific
      ch.forEach(function(e) {
        if (e.collection_id === cid) {
           new_ch.unshift(e);
        }
      });

      return new_ch;
    },
  },
  watch: {
    selectedCohort(newCohort) {
      this.setCohort(newCohort);
    },
    cohort() {
      this.selectedCohort = this.cohort;
    },
  },
  created() {
    this.fetchCohorts();
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCohorts: actions.FETCH_COHORTS,
      setCohort: actions.SET_COHORT,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
