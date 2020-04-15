<template>
  <section>
    <v-toolbar card dense flat :class="getToolbarClass()" class="rounded-lg">
      <v-toolbar-items>
        <input-variables-dialog @dialogOpened="opened" />
      </v-toolbar-items>
      <v-divider vertical class="ml-4"></v-divider>
      <v-chip
        v-if="inputVariables.length == 0"
        disabled
        color="primary"
        class="white--text title"
        >No variables selected</v-chip
      >
      <v-chip v-else disabled color="primary" class="white--text title"
        >{{ inputVariables.length }} variable<span
          v-if="inputVariables.length != 1"
          >s</span
        >&nbsp;selected</v-chip
      >
      <v-spacer />
      <v-toolbar-items>
        <v-chip
          disabled
          class="white--text title"
          :style="'background: ' + colors['cohort']"
          >Selected Cohort - {{ animatedNumber }}</v-chip
        >
        <v-chip
          disabled
          class="primary--text title"
          :style="'background: ' + colors['population']"
          >Study Population - {{ unfilteredData.length }}</v-chip
        >
      </v-toolbar-items>
      <v-toolbar-items>
        <v-icon v-if="expanded" @click="expandClicked">expand_less</v-icon>
        <v-icon v-else @click="expandClicked">expand_more</v-icon>
      </v-toolbar-items>
      <!-- <v-spacer></v-spacer>
      <v-select
        :items="['Cohort']"
        menu-props="auto"
        label="Select"
        hide-details
        append-icon="format_color_fill"
        color="primary"
      ></v-select> -->
      <!-- <v-spacer></v-spacer> -->
      <!--
      <v-divider vertical class="mr-4"></v-divider>
      <v-toolbar-items class="scrollable">
        <v-tooltip color="primary" top>
          <template v-slot:activator="{ on }">
            <span class="primary--text title mt-3" v-on="on"
              >{{ animatedNumber }}/{{ unfilteredData.length }}</span
            >
          </template>
          <span>Number of subjects in cohort.</span>
        </v-tooltip>
      </v-toolbar-items>
-->
    </v-toolbar>
    <v-divider></v-divider>
  </section>
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
    filteredData(oldData, newData) {
      const startValue = newData.length;
      const endValue = oldData.length;
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
