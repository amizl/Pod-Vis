<template>
  <div style="background: white">
    <v-stepper v-model="stepnum" :value="stepnum" alt-labels>
      <v-stepper-header>
        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 1"
            step="1"
            :style="stepStyle('1')"
            :class="stepClass('1')"
            style="text-align: center;"
            >Home Page
          </v-stepper-step>
          <span>{{ step_descr['1'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 2"
            step="2"
            :style="stepStyle('2')"
            :class="stepClass('2')"
            >Dataset Manager
          </v-stepper-step>
          <span>{{ step_descr['2'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 3"
            step="3"
            :style="stepStyle('3')"
            :class="stepClass('3')"
            >Cohort Manager
          </v-stepper-step>
          <span>{{ step_descr['3'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 4"
            step="4"
            :style="stepStyle('4')"
            :class="stepClass('4')"
            >Data Explorer
          </v-stepper-step>
          <span>{{ step_descr['4'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 5"
            step="5"
            :style="stepStyle('5')"
            :class="stepClass('5')"
            >Summary Matrix
          </v-stepper-step>
          <span>{{ step_descr['5'] }}</span>
        </v-tooltip>
      </v-stepper-header>
      <v-stepper-items>
        <v-stepper-content step="1" :style="stepStyle('1')">
          <v-btn color="primary" @click="stepTwo()">BEGIN</v-btn>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>

    <!-- substep trackers -->
    <v-stepper
      v-if="step === '2'"
      :value="substepnum"
      model="substepnum"
      :style="currentStepStyle"
    >
      <v-stepper-header>
        <v-stepper-step
          :complete="substepnum !== '2.1' || stepnum === '3'"
          step="2.1"
          >Choose Datasets
          <small class="primary--text"
            >Select one or more datasets and click on "SELECT VARIABLES"</small
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substepnum === '2.3' || stepnum === '3'"
          step="2.2"
          >Select Variables
          <small class="primary--text"
            >Select one or more variables and click on "SAVE STUDY
            DATASET"</small
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="stepnum === '3'" step="2.3"
          >Save (and name) Study Dataset</v-stepper-step
        >
      </v-stepper-header>
    </v-stepper>

    <v-stepper
      v-if="step === '3'"
      :value="substepnum"
      model="substepnum"
      :style="currentStepStyle"
    >
      <v-stepper-header>
        <v-stepper-step :complete="inputVariables.length > 0" step="3.1"
          >Choose Predictor Variables</v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="outputVariables.length > 0" step="3.2"
          >Choose Outcome Variables</v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="filteredData.length < unfilteredData.length"
          step="3.3"
          >Apply Filters to Variables</v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step step="3.4">Save Cohort</v-stepper-step>
      </v-stepper-header>
    </v-stepper>

    <v-stepper
      v-if="step === '4'"
      :value="substepnum"
      model="substepnum"
      :style="currentStepStyle"
    >
      <v-stepper-header>
        <v-stepper-step step="4.1"
          >Choose your timeframe - not yet implemented</v-stepper-step
        >
        <v-divider></v-divider>
      </v-stepper-header>
    </v-stepper>

    <v-stepper
      v-if="step === '5'"
      :value="substepnum"
      model="substepnum"
      :style="currentStepStyle"
    >
      <v-stepper-header>
        <v-stepper-step step="5.1"
          >Review a log of previous analyses</v-stepper-step
        >
        <v-divider></v-divider>
      </v-stepper-header>
    </v-stepper>
  </div>
</template>
<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';

export default {
  props: {
    step: {
      type: String,
      required: true,
    },
    substep: {
      type: String,
      required: true,
    },
    currentStepStyle: {
      type: String,
      default:
        'background: rgb(100,100,200,0.08); border-left: 1px dotted black; border-right: 1px dotted black; border-top: 1px dotted black;',
      required: false,
    },
  },
  data() {
    return {
      stepnum: '',
      substepnum: '',
      step_descr: {
        '1': 'Archive of Uploaded Datasets',
        '2': 'Create your study dataset',
        '3': 'Design your query: Choose predictors and outcomes',
        '4': 'Choose your timeframe',
        '5': 'Review a log of your previous analyses',
      },
      expanded: true,
    };
  },
  watch: {
    step() {
      this.stepnum = this.step;
    },
    substep() {
      this.substepnum = this.substep;
    },
  },
  created() {
    this.stepnum = this.step;
    this.substepnum = this.substep;
  },
  computed: {
    ...mapState('cohortManager', {
      inputVariables: state.INPUT_VARIABLES,
      outputVariables: state.OUTPUT_VARIABLES,
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
    }),
  },
  methods: {
    stepTwo() {
      this.$router.push('/datasets');
    },
    stepStyle(step) {
      if (step === this.stepnum) {
        return this.currentStepStyle;
      } else {
        return '';
      }
    },
    stepClass(step) {
      return 'pb-2';
    },
  },
};
</script>
