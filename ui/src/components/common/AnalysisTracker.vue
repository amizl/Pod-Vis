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
            @click.native="gotoHomepage()"
            >Home Page
          </v-stepper-step>
          <span class="subtitle-1">{{ step_descr['1'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 2"
            step="2"
            :style="stepStyle('2')"
            :class="stepClass('2')"
            @click.native="gotoDatasetManager()"
            >Dataset Manager
          </v-stepper-step>
          <span class="subtitle-1">{{ step_descr['2'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 3"
            step="3"
            :style="stepStyle('3')"
            :class="stepClass('3')"
            @click.native="gotoCohortManager()"
            >Cohort Manager
          </v-stepper-step>
          <span class="subtitle-1">{{ step_descr['3'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 4"
            step="4"
            :style="stepStyle('4')"
            :class="stepClass('4')"
            @click.native="gotoDataExplorer()"
            >Data Explorer
          </v-stepper-step>
          <span class="subtitle-1">{{ step_descr['4'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="stepnum > 5"
            step="5"
            :style="stepStyle('5')"
            :class="stepClass('5')"
            @click.native="gotoSummaryMatrix()"
            >Summary Matrix
          </v-stepper-step>
          <span class="subtitle-1">{{ step_descr['5'] }}</span>
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
          <span
            >Select one or more datasets and click on "SELECT VARIABLES"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substepnum === '2.3' || stepnum === '3'"
          step="2.2"
          >Select Variables
          <span
            >Select one or more variables and click on "SAVE STUDY
            DATASET"</span
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
    <error-dialog
      :show="show_error_dialog"
      :error-message="error_message"
      @closed="show_error_dialog = false"
    ></error-dialog>
    <confirmation-dialog
      :show="show_confirmation_dialog"
      :confirmation-message="confirmation_message"
      :target-uri="target_uri"
      @closed="show_confirmation_dialog = false"
    ></confirmation-dialog>
  </div>
</template>
<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import ErrorDialog from '@/components/common/ErrorDialog.vue';
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue';

export default {
  components: {
    ErrorDialog,
    ConfirmationDialog,
  },
  props: {
    step: {
      type: String,
      required: true,
    },
    substep: {
      type: String,
      required: true,
    },
    collectionId: {
      type: Number,
      required: false,
    },
    currentStepStyle: {
      type: String,
      default:
        'background: rgb(212,197,71,0.2); border-left: 1px dotted black; border-right: 1px dotted black; border-top: 1px dotted black;',
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

      // ErrorDialog
      error_message: '',
      show_error_dialog: false,

      // ConfirmationDialog
      confirmation_message: '',
      show_confirmation_dialog: false,
      target_uri: '',
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
        return this.currentStepStyle + ' cursor: pointer;';
      } else {
        return 'cursor: pointer;';
      }
    },
    stepClass(step) {
      return 'pb-2';
    },
    gotoHomepage() {
      if (this.stepnum === 1) {
        // no-op
      } else if (this.stepnum > 2) {
        this.displayConfirmationDialog(
          'Are you sure you want to return to the home page? ' +
            'Any unsaved work in progress on the current study dataset will be lost.',
          'homepage'
        );
      } else {
        this.$router.push(`homepage`);
      }
    },
    gotoDatasetManager() {
      if (this.stepnum === 2) {
        // no-op
      } else if (this.stepnum > 2) {
        this.displayConfirmationDialog(
          'Are you sure you want to return to the Dataset Manager? ' +
            'Any unsaved work in progress on the current study dataset will be lost.',
          'datasets'
        );
      } else {
        this.$router.push(`datasets`);
      }
    },
    gotoCohortManager() {
      if (this.stepnum === 3) {
        // no-op
      } else if (this.stepnum <= 2) {
        this.displayErrorDialog(
          'A study dataset must be created before the Cohort Manager can be used. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else {
        this.$router.push(`cohorts?collection=${this.collectionId}`);
      }
    },
    gotoDataExplorer() {
      if (this.stepnum === 4) {
        // no-op
      } else if (this.stepnum <= 2) {
        this.displayErrorDialog(
          'A study dataset must be created before the Data Explorer can be used. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else {
        this.$router.push(`explore?collection=${this.collectionId}`);
      }
    },
    gotoSummaryMatrix() {
      if (this.stepnum === 5) {
        // no-op
      } else if (this.stepnum <= 2) {
        this.displayErrorDialog(
          'A study dataset must be created before the Summary Matrix can be viewed. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else {
        this.$router.push(`summary?collection=${this.collectionId}`);
      }
    },
    displayErrorDialog(errorMsg) {
      this.error_message = errorMsg;
      this.show_error_dialog = true;
    },
    displayConfirmationDialog(confirmationMsg, targetUri) {
      this.confirmation_message = confirmationMsg;
      this.target_uri = targetUri;
      this.show_confirmation_dialog = true;
    },
  },
};
</script>
