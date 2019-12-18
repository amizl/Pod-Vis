<template>
  <div>
    <v-stepper v-model="stepnum" :value="stepnum">
      <v-stepper-header>
        <v-stepper-step :complete="stepnum > 1" step="1"
          >Home Page <small>Archive of Uploaded Datasets</small></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="stepnum > 2" step="2"
          >Dataset Manager
          <small>Create your study dataset</small></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="stepnum > 3" step="3"
          >Cohort Manager
          <small
            >Design your query: Choose predictors and outcomes</small
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="stepnum > 4" step="4"
          >Data Explorer <small>Choose your timeframe</small></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="stepnum > 5" step="5"
          >Summary Matrix
          <small>Review a log of your previous analyses</small></v-stepper-step
        >
      </v-stepper-header>
      <v-stepper-items>
        <v-stepper-content step="1">
          <v-btn color="primary" @click="stepTwo()">BEGIN</v-btn>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>

    <!-- substep trackers -->
    <v-stepper v-if="step === '2'" :value="substepnum" model="substepnum">
      <v-stepper-header>
        <v-stepper-step
          :complete="substepnum !== '2.1' || stepnum === '3'"
          step="2.1"
          >Choose Datasets
          <small
            >Select one or more datasets and click on "SELECT VARIABLES"</small
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substepnum === '2.3' || stepnum === '3'"
          step="2.2"
          >Select Variables
          <small
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

    <v-stepper v-if="step === '3'" value="3.1" model="substepnum">
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

    <v-stepper v-if="step === '4'" value="4.1" model="substepnum">
      <v-stepper-header>
        <v-stepper-step step="4.1"
          >Choose your timeframe - not yet implemented</v-stepper-step
        >
        <v-divider></v-divider>
      </v-stepper-header>
    </v-stepper>

    <v-stepper v-if="step === '5'" value="5.1" model="substepnum">
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
  },
  data() {
    return {
      stepnum: '',
      substepnum: '',
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
  },
};
</script>
