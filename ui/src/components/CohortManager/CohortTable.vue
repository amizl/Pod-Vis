<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table v-else :headers="headers" :items="cohorts" item-key="label">
    <template v-slot:items="props">
      <tr>
        <td class="text-xs-left">{{ props.item.label }}</td>
      </tr>
    </template>
    <template v-slot:no-data>
      <v-alert :value="true" color="info" icon="info">
        You have no saved cohorts.
      </v-alert>
    </template>
  </v-data-table>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  data() {
    return {
      headers: [
        {
          text: 'Cohort Name',
          value: 'label',
        },
      ],
    };
  },
  computed: {
    ...mapState('cohortManager', {
      isLoading: state.IS_LOADING,
      cohorts: state.COHORTS,
    }),
  },
  created() {
    if (!this.cohorts.length) this.fetchCohorts();
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCohorts: actions.FETCH_COHORTS,
    }),
  },
};
</script>

<style></style>
