<template>
  <section>
    <v-data-table
      v-if="timesBetweenVisits"
      :headers="headers"
      :items="timesBetweenVisits"
      dense
      hide-default-footer
      disable-pagination
    >
      <template v-slot:item="props">
        <tr>
          <td class="text-xs-left">
            {{ props.item.is_first ? props.item.study_name : '' }}
          </td>
          <td class="text-xs-left">
            {{ props.item.is_first ? props.item.n_subjects : '' }}
          </td>
          <td class="text-xs-left">{{ props.item.first_visit }}</td>
          <td class="text-xs-left">{{ props.item.last_visit }}</td>
          <td class="text-xs-left">{{ props.item.n_variables }}</td>
          <td class="text-xs-left">
            {{ props.item.avg_time_secs | formatTime }}
          </td>
        </tr>
      </template>
    </v-data-table>
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
          text: 'First Visit',
          align: 'left',
          sortable: true,
          value: 'first_visit',
        },
        {
          text: 'Last Visit',
          align: 'left',
          sortable: true,
          value: 'last_visit',
        },
        {
          text: 'Variables',
          align: 'left',
          sortable: true,
          value: 'n_variables',
        },
        {
          text: 'Average Time',
          align: 'left',
          sortable: true,
          value: 'avg_time_secs',
        },
      ],
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
