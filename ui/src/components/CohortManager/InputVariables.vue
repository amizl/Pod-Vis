<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow pa-0 ma-0">
    <input-variables-toolbar
      :expanded="expanded"
      :highlighted="highlighted"
      class="ma-0 pa-0"
      @expandClicked="expandClicked"
    />
    <v-container v-show="expanded" fluid fill-width class="pa-0 ma-0">
      <v-row class="pa-0 ma-0">
        <v-col cols="12">
          <input-variables-charts v-if="hasUserAddedInputVariables" />
          <v-subheader
            v-else
            class="subheading primary--text text--lighten-4 text-h6"
          >
            ADD PREDICTOR VARIABLES
          </v-subheader>
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
</template>

<script>
import { mapMutations, mapState } from 'vuex';
import { mutations, state } from '@/store/modules/cohortManager/types';
import InputVariablesToolbar from '@/components/CohortManager/InputVariablesToolbar.vue';
import InputVariablesCharts from '@/components/CohortManager/InputVariablesCharts.vue';

export default {
  components: {
    InputVariablesToolbar,
    InputVariablesCharts,
  },
  props: {
    expanded: {
      type: Boolean,
      required: true,
    },
    highlighted: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      variables: [],
      value: [],
    };
  },
  computed: {
    ...mapState('cohortManager', {
      inputVariables: state.INPUT_VARIABLES,
    }),
    hasUserAddedInputVariables() {
      return this.inputVariables.length > 0;
    },
  },
  methods: {
    ...mapMutations('cohortManager', {
      addInputVariable: mutations.ADD_INPUT_VARIABLE,
      removeInputVariable: mutations.REMOVE_INPUT_VARIABLE,
    }),
    expandClicked(newval) {
      this.$emit('update:expanded', newval);
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
</style>
