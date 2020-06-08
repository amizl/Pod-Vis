<template>
  <section>
    <v-chip
      v-for="tbv in timesBetweenVisits"
      :disabled="true"
      class="primary--text title mb-3"
      :style="'background: ' + colors['population']"
      >{{ tbv.study_name }} - {{ tbv.n_subjects }} subject(s) -
      {{ tbv.avg_time_secs | formatTime }}</v-chip
    >
  </section>
</template>

<script>
import axios from 'axios';
import { mapState, mapMutations } from 'vuex';
import { state, actions } from '@/store/modules/dataSummary/types';
import { colors } from '@/utils/colors';
import { format } from 'd3-format';

export default {
  filters: {
    formatTime(tsecs) {
      var tdays = tsecs / (3600 * 24);
      var tyears = tdays / 365.25;
      if (tdays <= 60) {
        return format('.1f')(tdays) + ' days';
      } else {
        return format('.1f')(tyears) + ' year(s)';
      }
    },
  },
  data() {
    return {
      headers: [
        {
          text: 'Study',
          align: 'left',
          sortable: true,
          value: 'study_name',
        },
        {
          text: 'Subject Count',
          align: 'left',
          sortable: true,
          value: 'n_subjects',
        },
        {
          text: 'Average Time',
          align: 'left',
          sortable: true,
          value: 'avg_time_secs',
        },
      ],
      pagination: {
        rowsPerPage: -1,
      },
      colors: colors,
    };
  },
  computed: {
    ...mapState('dataSummary', {
      timesBetweenVisits: state.TIMES_BETWEEN_VISITS,
    }),
  },
};
</script>

<style scoped></style>
