<template>
  <div>
    <v-container
      v-for="(a, anum) in analyses"
      fluid
      fill-width
      class="ma-0 pa-0 my-3"
    >
      <v-row class="ma-0 pa-0">
        <v-col class="ma-0 pa-0">
          <analysis
	    :id="'analysis-' + a.index"
            :analysis="a"
            :title="'ANALYSIS #' + a.index"
            @deleteAnalysis="deleteAnalysis(anum)"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import CohortTable from '@/components/common/CohortTable.vue';
import Analysis from '@/components/DataExplorer/Analysis.vue';
import AnalyticsPanel from '@/components/DataExplorer/AnalyticsPanel.vue';
import DetailedView from '@/components/DataExplorer/DetailedView.vue';
import { colors } from '@/utils/colors';

export default {
  components: {
    Analysis,
  },
  props: {
    analyses: {
      type: Array,
      required: false,
      default: [],
    },
  },
  data() {
    return {
      expanded: true,
    };
  },
  methods: {
    deleteAnalysis(anum) {
      this.$emit('deleteAnalysis', anum);
    },
  },
};
</script>
