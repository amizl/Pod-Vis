<template>
  <div style="background: white">
    <v-stepper v-model="step" :value="step" alt-labels>
      <v-stepper-header>
        <v-stepper-step
          :complete="step > 1"
          step="1"
          :style="stepStyle('1')"
          :class="stepClass('1')"
          @click.native="gotoDatasetManager()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }">{{
                step > 1
                  ? 'Study&nbsp;dataset&nbsp;created'
                  : 'Create&nbsp;study&nbsp;dataset'
              }}</span>
            </template>
            <span class="subtitle-1">{{ step_descr['1'] }}</span>
          </v-tooltip>
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="step > 2"
          step="2"
          :style="stepStyle('2')"
          :class="stepClass('2')"
          @click.native="gotoCohortManager()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }">{{
                step > 2 ? 'Cohorts&nbsp;created' : 'Manage&nbsp;cohorts'
              }}</span>
            </template>
            <span class="subtitle-1">{{ step_descr['2'] }}</span>
          </v-tooltip>
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="step > 3"
          step="3"
          :style="stepStyle('3')"
          :class="stepClass('3')"
          @click.native="gotoDataExplorer()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }"
                >Data&nbsp;Analytics</span
              >
            </template>
            <span class="subtitle-1">{{ step_descr['3'] }}</span>
          </v-tooltip>
        </v-stepper-step>
      </v-stepper-header>
    </v-stepper>

    <!-- substep trackers -->
    <!-- step 1 - automated analysis mode -->
    <v-stepper
      v-if="step === '1' && automatedAnalysisMode"
      :value="substep"
      model="substep"
    >
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step
          :class="substepClass('1.1')"
          :complete="substep !== '1.1' || step === '2'"
          step="1.1"
          @click.native="substepClicked('1.1')"
          ><span class="subtitle-1">Choose Datasets</span>
          <span
            >Choose datasets and click "SELECT VARIABLES"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substep === '1.3' || substep === '1.4' || step === '2'"
          step="1.2"
          :class="substepClass('1.2')"
          @click.native="substepClicked('1.2')"
          ><span class="subtitle-1">Select Variables</span>
          <span
            >Select predictor and output variables and click on "BEGIN AUTOMATED
            ANALYSIS"</span
          ></v-stepper-step
        >
      </v-stepper-header>
    </v-stepper>

    <!-- step 1 - manual analysis mode -->
    <v-stepper
      v-if="step === '1' && !automatedAnalysisMode"
      :value="substep"
      model="substep"
    >
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step
          :class="substepClass('1.1')"
          :complete="substep !== '1.1' || step === '2'"
          step="1.1"
          @click.native="substepClicked('1.1')"
          ><span class="subtitle-1">Choose Datasets</span>
          <span
            >Choose datasets and click "SELECT VARIABLES"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substep === '1.3' || substep === '1.4' || step === '2'"
          step="1.2"
          :class="substepClass('1.2')"
          @click.native="substepClicked('1.2')"
          ><span class="subtitle-1">Select Variables</span>
          <span
            >Select variables and click on "SAVE STUDY DATASET"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substep === '1.4' || step === '2'"
          step="1.3"
          :class="substepClass('1.3')"
          @click.native="substepClicked('1.3')"
          ><span class="subtitle-1">Save Study Dataset</span></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step === '2'"
          step="1.4"
          :class="substepClass('1.4')"
          @click.native="substepClicked('1.4')"
          ><span class="subtitle-1"
            >Choose First & Last Visit</span
          ></v-stepper-step
        >
      </v-stepper-header>
    </v-stepper>

    <v-stepper v-if="step === '2'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step
          :complete="inputVariables.length > 0 || substep >= 2.4"
          step="2.1"
          :class="substepClass('2.1')"
          @click.native="substepClicked('2.1')"
          ><span class="subtitle-1"
            >Choose predictor variables</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="outputVariables.length > 0 || substep >= 2.4"
          step="2.2"
          :class="substepClass('2.2')"
          @click.native="substepClicked('2.2')"
          ><span class="subtitle-1"
            >Choose outcome variables</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="
            filteredData.length < unfilteredData.length || substep >= 2.4
          "
          step="2.3"
          :class="substepClass('2.3')"
          @click.native="substepClicked('2.3')"
          >{{
            filteredData.length == unfilteredData.length
              ? 'Apply filters to define cohorts'
              : 'Filters applied; review charts and analytics'
          }}</v-stepper-step
        >
      </v-stepper-header>
    </v-stepper>

    <v-stepper v-if="step === '3'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step
          step="3.1"
          :class="substepClass('3.1')"
          :complete="substep === '3.2'"
          @click.native="substepClicked('3.1')"
          ><span class="subtitle-1">Select two or more cohorts.</span>
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          step="3.2"
          :class="substepClass('3.2')"
          @click.native="substepClicked('3.2')"
          ><span class="subtitle-1">Click on 'ANALYZE SELECTED COHORTS'</span>
        </v-stepper-step>
      </v-stepper-header>
    </v-stepper>

    <error-dialog
      :show="show_error_dialog"
      :error-title="error_title"
      :error-message="error_message"
      @closed="show_error_dialog = false"
    ></error-dialog>
    <confirmation-dialog
      :show="show_confirmation_dialog"
      :confirmation-title="confirmation_title"
      :confirmation-message="confirmation_message"
      :target-uri="target_uri"
      @closed="show_confirmation_dialog = false"
    ></confirmation-dialog>
  </div>
</template>
<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';
import { state as dsState } from '@/store/modules/dataSummary/types';
import ErrorDialog from '@/components/common/ErrorDialog.vue';
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue';
import logEvent from '@/utils/logging';

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
      default: -1,
    },
    automatedAnalysisMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      step_descr: {
        '1': 'Create your study dataset',
        '2': 'Design your query: Choose predictors and outcomes',
        '3': 'Analyze your data: Analyze cohorts and variables.',
      },
      expanded: true,

      // ErrorDialog
      error_title: '',
      error_message: '',
      show_error_dialog: false,

      // ConfirmationDialog
      confirmation_title: '',
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
      cohorts: state.COHORTS,
      collection: state.COLLECTION,
      helpMode: state.HELP_MODE,
    }),
    ...mapState('dataSummary', {
      dsCollection: dsState.COLLECTION,
    }),
    // cohorts are collection-specific
    collection_cohorts() {
      const cch = [];
      const cid = this.collection.id;

      this.cohorts.forEach(e => {
        if (e.collection_id === cid) {
          cch.push(e);
        }
      });

      return cch;
    },
  },
  watch: {
    substep(nss) {
      logEvent(
        this.$gtag,
        null,
        null,
        'tracker_step',
        'workflow_transition',
        nss
      );
    },
  },
  mounted() {
    logEvent(
      this.$gtag,
      null,
      null,
      'tracker_step',
      'workflow_transition',
      this.substep
    );
  },
  methods: {
    stepTwo() {
      this.$router.push('/datasets');
    },
    stepStyle() {
      return 'cursor: pointer;';
    },
    stepClass(step) {
      if (step === this.step) {
        return 'tracker_step_highlight pa-3';
      } else {
        return 'pa-3';
      }
    },
    substepClass(substep) {
      var cl = 'px-5';
      if (this.helpMode && this.substep == substep) {
        cl = cl + ' help_mode';
      }
      return cl;
    },
    // Transitions between major steps
    gotoHomepage() {
      if (this.step == 1) {
        // no-op
      } else if (this.step > 2) {
        this.displayConfirmationDialog(
          'Return to Home Page?',
          'Are you sure you want to return to the home page? ' +
            'Any unsaved work in progress on the current study dataset will be lost.',
          'homepage'
        );
      } else {
        this.$router.push(`homepage`);
      }
    },
    gotoDatasetManager() {
      logEvent(this.$gtag, null, null, 'tracker_clicked', 'click', '1');
      if (this.step == 1) {
        // no-op
      } else if (this.step > 1) {
        this.displayConfirmationDialog(
          'Return to Dataset Manager?',
          'Are you sure you want to return to the Dataset Manager? ' +
            'Any unsaved work in progress on the current study dataset will be lost.',
          'datasets'
        );
      } else {
        this.$router.push(`datasets`);
      }
    },
    gotoCohortManager() {
      logEvent(this.$gtag, null, null, 'tracker_clicked', 'click', '2');
      if (this.step == 2) {
        // no-op
      } else if (this.step == 1 && this.substep == 1.4) {
        if (!this.dsCollection.has_visits_set) {
          this.displayErrorDialog(
            'First/Last Visits Not Selected',
            'First and last visits must be selected before the Cohort Manager can be used. ' +
              "Please finish selecting the first and last visits or return to the home page and use the 'Add Cohorts' " +
              'link for an existing study dataset.'
          );
        } else {
          this.$router.push(`cohorts?collection=${this.collectionId}`);
        }
      } else if (this.step <= 1) {
        this.displayErrorDialog(
          'No Study Dataset',
          'A study dataset must be created before the Cohort Manager can be used. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else {
        this.$router.push(`cohorts?collection=${this.collectionId}`);
      }
    },
    gotoDataExplorer() {
      logEvent(this.$gtag, null, null, 'tracker_clicked', 'click', '3');
      if (this.step == 3) {
        // no-op
      } else if (this.step <= 1) {
        this.displayErrorDialog(
          'No Study Dataset',
          'A study dataset must be created before Data Analytics can be performed. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else if (this.collection_cohorts.length < 2) {
        this.displayErrorDialog(
          'Too Few Cohorts',
          'At least two cohorts must be created before proceeding to Data Analytics.'
        );
      } else {
        this.$emit('nextStep', true);
      }
    },
    substepClicked(substep) {
      logEvent(this.$gtag, null, null, 'tracker_clicked', 'click', substep);
    },
    // Cohort Manager sub-step transitions.
    goto2p1() {
      this.$emit('update:substep', '2.1');
    },
    createNew() {
      this.$emit('createNew', true);
    },
    createSimilar() {
      this.$emit('createSimilar', true);
    },
    goto2p2() {
      if (this.inputVariables.length > 0) {
        this.$emit('update:substep', '2.2');
      } else {
        this.displayErrorDialog(
          'No Predictor Variables',
          'At least one predictor variable must be selected before continuing to the next step.'
        );
      }
    },
    goto2p3() {
      if (this.outputVariables.length > 0) {
        this.$emit('update:substep', '2.3');
      } else {
        this.displayErrorDialog(
          'No Outcome Variables',
          'At least one outcome variable must be selected before continuing to the next step.'
        );
      }
    },
    displayErrorDialog(errorTitle, errorMsg) {
      this.error_title = errorTitle;
      this.error_message = errorMsg;
      this.show_error_dialog = true;
    },
    displayConfirmationDialog(confirmationTitle, confirmationMsg, targetUri) {
      this.confirmation_title = confirmationTitle;
      this.confirmation_message = confirmationMsg;
      this.target_uri = targetUri;
      this.show_confirmation_dialog = true;
    },
  },
};
</script>
