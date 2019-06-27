<template>
  <section>
    <v-toolbar card dense flat color="white rounded-lg">
      <v-toolbar-items> <input-variables-dialog /> </v-toolbar-items>
      <v-divider vertical class="ml-4"></v-divider>
      <v-spacer></v-spacer>
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
    </v-toolbar>
    <v-divider></v-divider>
  </section>
</template>

<script>
import InputVariablesDialog from '@/components/CohortManager/InputVariablesDialog.vue';
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';
import TWEEN from '@tweenjs/tween.js';

export default {
  components: {
    InputVariablesDialog,
  },
  data() {
    return {
      tweenData: 0,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
    }),
    animatedNumber() {
      return this.tweenData.toFixed(0);
    },
  },
  watch: {
    filteredData(oldData, newData) {
      let startValue = newData.length;
      let endValue = oldData.length;
      var vm = this;
      function animate() {
        if (TWEEN.update()) {
          requestAnimationFrame(animate);
        }
      }
      new TWEEN.Tween({ tweeningValue: startValue })
        .to({ tweeningValue: endValue }, 1000)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onUpdate(({ tweeningValue }) => {
          vm['tweenData'] = tweeningValue;
        })
        .start();
      animate();
    },
  },
  created() {
    this.tweenData = this.filteredData.length;
  },
  methods: {
    tween(startValue, endValue, prop) {
      var vm = this;
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
