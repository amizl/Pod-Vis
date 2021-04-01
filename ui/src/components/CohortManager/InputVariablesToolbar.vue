<template>
  <v-container fluid fill-width class="ma-0 pa-0">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <v-card color="#eeeeee">
          <v-card-title class="primary--text pl-3 py-2">
            <input-variables-dialog
              ref="input_dialog"
              :show-all-vars-checkbox="false"
              @dialogOpened="opened"
              @userSelectedInputVariables="userSelectedInputVariables"
            />

            <v-divider vertical class="ml-4 mr-4"> </v-divider>

            <v-tooltip bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span
                  v-on="{ ...tooltip }"
                  @click="$refs.input_dialog.openInputVariableDialog = true"
                >
                  <v-chip
                    label
                    color="primary"
                    class="white--text title mr-2"
                    >{{ inputVariables.length }}</v-chip
                  >
                  <span class="black--text text-body-1"
                    >Variable{{ inputVariables.length == 1 ? '' : 's' }}</span
                  >
                </span>
              </template>
              <span class="subtitle-1">
                {{ inputVariables.length }} predictor variable{{
                  inputVariables.length == 1 ? '' : 's'
                }}
                selected
              </span>
            </v-tooltip>

            <v-tooltip bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span v-on="{ ...tooltip }">
                  <v-chip
                    label
                    color="primary"
                    class="white--text title mr-2 ml-5"
                    :style="'background: ' + colors['cohort']"
                    >{{ animatedNumber }}</v-chip
                  >
                  <span class="black--text text-body-1">Cohort</span>
                </span>
              </template>
              <span class="subtitle-1">
                {{ animatedNumber }} subject{{
                  animatedNumber == 1 ? '' : 's'
                }}
                in selected cohort
              </span>
            </v-tooltip>

            <v-tooltip bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span v-on="{ ...tooltip }">
                  <v-chip
                    label
                    class="black--text title mr-2 ml-5"
                    :style="'background: ' + colors['population']"
                    >{{ unfilteredData.length }}</v-chip
                  >
                  <span class="black--text text-body-1">Population</span>
                </span>
              </template>
              <span class="subtitle-1">
                {{ unfilteredData.length }} subject{{
                  unfilteredData.length == 1 ? '' : 's'
                }}
                in study population
              </span>
            </v-tooltip>

            <v-spacer />

            <v-switch
              v-model="useLongScaleNamesSelect"
              label="Use long variable names"
              class="pa-0 ma-0 pr-3"
              hide-details
            ></v-switch>

            <!--
            <v-toolbar-items>
              <v-icon v-if="expanded" @click="expandClicked"
                >expand_less</v-icon
              >
              <v-icon v-else @click="expandClicked">expand_more</v-icon>
            </v-toolbar-items>
-->
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>
  </v-container>

  <!--    <v-app-bar dense flat :class="getToolbarClass()" class="rounded-lg"> -->
</template>

<script>
import InputVariablesDialog from '@/components/CohortManager/InputVariablesDialog.vue';
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';
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
      useLongScaleNames: state.USE_LONG_SCALE_NAMES,
    }),
    animatedNumber() {
      return this.tweenData.toFixed(0);
    },
    useLongScaleNamesSelect: {
      get() {
        return this.useLongScaleNames;
      },
      set(value) {
        this.setUseLongScaleNames(value);
      },
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
    this.useLongScaleNamesSelect = this.useLongScaleNames;
  },
  methods: {
    ...mapActions('cohortManager', {
      setUseLongScaleNames: actions.SET_USE_LONG_SCALE_NAMES,
    }),
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
