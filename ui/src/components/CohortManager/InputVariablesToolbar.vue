<template>
  <v-container fluid fill-width class="ma-0 pa-0">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <v-card color="#eeeeee">
          <v-card-title class="primary--text pl-3 py-2">
            <input-variables-dialog
              @dialogOpened="opened"
              @userSelectedInputVariables="userSelectedInputVariables"
	      :showAllVarsCheckbox="false"
            />

            <v-divider vertical class="ml-4 mr-4"> </v-divider>

            <v-chip
              v-if="inputVariables.length == 0"
              color="primary"
              class="white--text title"
              >No variables selected</v-chip
            >
            <v-chip v-else color="primary" class="white--text title"
              >{{ inputVariables.length }} variable<span
                v-if="inputVariables.length != 1"
                >s</span
              >&nbsp;selected</v-chip
            >

            <v-spacer />

            <v-chip
              class="white--text title"
              :style="'background: ' + colors['cohort']"
              >Selected Cohort - {{ animatedNumber }}</v-chip
            >
            <v-chip
              class="primary--text title"
              :style="'background: ' + colors['population']"
              >Study Population - {{ unfilteredData.length }}</v-chip
            >

            <v-toolbar-items>
              <v-icon v-if="expanded" @click="expandClicked"
                >expand_less</v-icon
              >
              <v-icon v-else @click="expandClicked">expand_more</v-icon>
            </v-toolbar-items>
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <!--    <v-app-bar dense flat :class="getToolbarClass()" class="rounded-lg"> -->
</template>

<script>
import InputVariablesDialog from '@/components/CohortManager/InputVariablesDialog.vue';
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';
import TWEEN from '@tweenjs/tween.js';
import { colors } from '@/utils/colors';

export default {
  components: {
    InputVariablesDialog,
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
      tweenData: 0,
      colors: colors,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      inputVariables: state.INPUT_VARIABLES,
    }),
    animatedNumber() {
      return this.tweenData.toFixed(0);
    },
  },
  watch: {
    filteredData(newData, oldData) {
      const startValue = oldData.length;
      const endValue = newData.length;
      const vm = this;
      function animate() {
        if (TWEEN.update()) {
          requestAnimationFrame(animate);
        }
      }
      new TWEEN.Tween({ tweeningValue: startValue })
        .to({ tweeningValue: endValue }, 1000)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onUpdate(({ tweeningValue }) => {
          vm.tweenData = tweeningValue;
        })
        .start();
      animate();
    },
  },
  created() {
    this.tweenData = this.filteredData.length;
  },
  methods: {
    expandClicked() {
      this.$emit('expandClicked', !this.expanded);
    },
    userSelectedInputVariables() {
      this.$emit('userSelectedInputVariables', true);
    },
    tween(startValue, endValue, prop) {
      const vm = this;
      function animate() {
        if (TWEEN.update()) {
          requestAnimationFrame(animate);
        }
      }
      new TWEEN.Tween({ tweeningValue: startValue })
        .to({ tweeningValue: endValue }, 500)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onUpdate(({ tweeningValue }) => {
          vm[prop] = tweeningValue;
        })
        .start();
      animate();
    },
    getToolbarClass() {
      if (this.highlighted) {
        return 'toolbar_step_highlight';
      } else {
        return '';
      }
    },
    opened() {
      this.$emit('expandClicked', true);
    },
  },
};
</script>

<style scoped>
.horizontal {
  display: flex;
}
.scrollable {
  overflow-x: auto;
}
.scrollable::-webkit-scrollbar {
  display: none;
}
</style>
