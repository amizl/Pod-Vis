<template>
  <div>
    <v-container
      v-for="(a, index) in analyses"
      :key="`vca-${index}`"
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
      required: false,
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
  },
};
</script>
