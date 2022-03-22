<template>
  <div>
    <v-container
      v-for="(a, index) in analyses"
      :key="`vca-${a.index}`"
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
            @deleteAnalysis="deleteAnalysis(index)"
            @cohortColorChange="updateCohortColor"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Analysis from '@/components/DataExplorer/Analysis.vue';

export default {
  components: {
    Analysis,
  },
  props: {
    analyses: {
      type: Array,
      requirEd: false,
      default: () => [],
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
    updateCohortColor(cc) {
      // propagate event
      this.$emit('cohortColorChange', { 'cohort': cc['cohort'], 'color': cc['color'] });
    },
  },
};
</script>
