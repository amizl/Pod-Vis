<template>
  <v-layout column fill-height class="ma-0 pa-0">
    <input-variables-toolbar
      :expanded="expanded"
      :highlighted="highlighted"
      @expandClicked="expandClicked"
    />
    <v-container v-show="expanded" fluid fill-height class="pa-0 pb-1">
      <input-variables-charts v-if="hasUserAddedInputVariables" />
      <v-layout v-else column align-center justify-center fill-height>
        <v-subheader class="display-1 primary--text text--lighten-5 my-5">
          ADD PREDICTOR VARIABLES
        </v-subheader>
      </v-layout>
    </v-container>
  </v-layout>
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
