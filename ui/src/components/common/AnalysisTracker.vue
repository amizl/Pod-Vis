<template>
  <div style="background: white">
    <v-stepper v-model="step" :value="step" alt-labels>
      <v-stepper-header>
        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="step > 1"
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
            :complete="step > 2"
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
            :complete="step > 3"
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
            :complete="step > 4"
            step="4"
            :style="stepStyle('4')"
            :class="stepClass('4')"
            @click.native="gotoSummaryMatrix()"
            >Summary Matrix
          </v-stepper-step>
          <span class="subtitle-1">{{ step_descr['4'] }}</span>
        </v-tooltip>

        <v-divider></v-divider>

        <v-tooltip color="primary" right>
          <v-stepper-step
            slot="activator"
            :complete="step > 5"
            step="5"
            :style="stepStyle('5')"
            :class="stepClass('5')"
            @click.native="gotoDataExplorer()"
            >Data Explorer
          </v-stepper-step>
          <span class="subtitle-1">{{ step_descr['5'] }}</span>
        </v-tooltip>
      </v-stepper-header>
      <v-stepper-items> </v-stepper-items>
    </v-stepper>

    <!-- substep trackers -->
    <v-stepper
      v-if="step === '2'"
      :value="substep"
      model="substep"
      :style="currentStepStyle"
    >
      <v-stepper-header>
        <v-stepper-step :complete="substep !== '2.1' || step === '3'" step="2.1"
          >Choose Datasets
          <span
            >Choose one or more datasets and click on "SELECT VARIABLES"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="substep === '2.3' || step === '3'" step="2.2"
          >Select Variables
          <span
            >Select one or more variables and click on "SAVE STUDY
            DATASET"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="step === '3'" step="2.3"
          >Save (and name) Study Dataset</v-stepper-step
        >
      </v-stepper-header>
    </v-stepper>

    <v-stepper
      v-if="step === '3'"
      :value="substep"
      model="substep"
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
      <v-stepper-items>
        <v-stepper-content step="3.1">
          Click on "CHOOSE PREDICTOR VARIABLES" below and select one or more
          variables, then click here to
          <v-btn @click="goto3p2()">Continue</v-btn>.
        </v-stepper-content>

        <v-stepper-content step="3.2">
          Click on "CHOOSE OUTCOME VARIABLES" below and select one or more
          variables, then click here to
          <v-btn @click="goto3p3()">Continue</v-btn>.
        </v-stepper-content>

        <v-stepper-content step="3.3">
          Apply filters to predictor variables to define the desired cohort,
          then click here to <v-btn @click="goto3p4()">Continue</v-btn>.
        </v-stepper-content>

        <v-stepper-content step="3.4">
          Click on "SAVE COHORT" in the toolbar above to name and save this
          cohort.
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>

    <v-stepper
      v-if="step === '4'"
      :value="substep"
      model="substep"
      :style="currentStepStyle"
    >
      <v-stepper-header>
        <v-stepper-step step="4.1"
          >Choose a variable from the One-Way ANOVA table (top), then click on
          one of the p-values in the Tukey/Range HSD test table (bottom) to
          compare those cohorts in the Data Explorer.</v-stepper-step
        >
        <v-divider></v-divider>
      </v-stepper-header>
    </v-stepper>

    <v-stepper
      v-if="step === '5'"
      :value="substep"
      model="substep"
      :style="currentStepStyle"
    >
      <v-stepper-header>
        <v-stepper-step step="5.1"
          >Explore all the data for a chosen variable and set of cohorts. Click
          on an outcome variable in the Summary View (top) then choose one or
          more cohorts to display in the Cohorts table below.</v-stepper-step
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
      step_descr: {
        '1': 'Archive of Uploaded Datasets',
        '2': 'Create your study dataset',
        '3': 'Design your query: Choose predictors and outcomes',
        '4': 'Compare cohorts in the Summary Matrix.',
        '5': 'Examine cohorts and variables in the Data Explorer.',
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
      if (step === this.step) {
        return this.currentStepStyle + ' cursor: pointer;';
      } else {
        return 'cursor: pointer;';
      }
    },
    stepClass(step) {
      return 'pb-2';
    },
    // Transitions between major steps
    gotoHomepage() {
      if (this.step === 1) {
        // no-op
      } else if (this.step > 2) {
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
      if (this.step === 2) {
        // no-op
      } else if (this.step > 2) {
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
      if (this.step === 3) {
        // no-op
      } else if (this.step <= 2) {
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
      if (this.step === 4) {
        // no-op
      } else if (this.step <= 2) {
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
      if (this.step === 5) {
        // no-op
      } else if (this.step <= 2) {
        this.displayErrorDialog(
          'A study dataset must be created before the Summary Matrix can be viewed. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else {
        this.$router.push(`summary?collection=${this.collectionId}`);
      }
    },
    // Cohort Manager sub-step transitions.
    goto3p2() {
      if (this.inputVariables.length > 0) {
        this.$emit('update:substep', '3.2');
      } else {
        this.displayErrorDialog(
          'At least one predictor variable must be selected before continuing to the next step.'
        );
      }
    },
    goto3p3() {
      if (this.outputVariables.length > 0) {
        this.$emit('update:substep', '3.3');
      } else {
        this.displayErrorDialog(
          'At least one outcome variable must be selected before continuing to the next step.'
        );
      }
    },
    goto3p4() {
      if (this.filteredData.length < this.unfilteredData.length) {
        this.$emit('update:substep', '3.4');
      } else {
        this.displayErrorDialog(
          'At least one filter must be added before continuing to the next step.'
        );
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
