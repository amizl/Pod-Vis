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
                >Analyze&nbsp;cohorts</span
              >
            </template>
            <span class="subtitle-1">{{ step_descr['3'] }}</span>
          </v-tooltip>
        </v-stepper-step>
      </v-stepper-header>
    </v-stepper>

    <!-- substep trackers -->
    <v-stepper v-if="step === '1'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step
          :class="substepClass('1.1')"
          :complete="substep !== '1.1' || step === '2'"
          step="1.1"
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
          ><span class="subtitle-1">Save Study Dataset</span></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="step === '2'"
          step="1.4"
          :class="substepClass('1.4')"
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
          ><span class="subtitle-1"
            >Choose predictor variables</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="outputVariables.length > 0 || substep >= 2.4"
          step="2.2"
          :class="substepClass('2.2')"
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
          >Apply filters to define cohorts</v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substep === '2.5'"
          step="2.4"
          :class="substepClass('2.4')"
          ><span class="subtitle-1"
            >Review charts and analytics</span
          ></v-stepper-step
        >
      </v-stepper-header>
    </v-stepper>

    <v-stepper v-if="step === '3'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step step="3.1"
          >Select the cohorts and scale (i.e., outcome variable) to display in
          the Detailed View by using the Cohorts Included in Analysis table
          (top) and the Analytics panel (bottom left), respectively. Use the
          checkboxes to control which cohorts appear in the Detailed View and
          click on the desired scale in the Analytics panel.
        </v-stepper-step>
        <v-divider></v-divider>
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
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import { state as dsState } from '@/store/modules/dataSummary/types';
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
  },
  data() {
    return {
      step_descr: {
        '1': 'Create your study dataset',
        '2': 'Design your query: Choose predictors and outcomes',
        '3': 'Analyze cohorts and variables in the Data Explorer.',
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
  methods: {
    stepTwo() {
      this.$router.push('/datasets');
    },
    stepStyle(step) {
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
      if (this.step == 3) {
        // no-op
      } else if (this.step <= 1) {
        this.displayErrorDialog(
          'No Study Dataset',
          'A study dataset must be created before the Data Explorer can be used. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else if (this.collection_cohorts.length < 2) {
        this.displayErrorDialog(
          'Too Few Cohorts',
          'At least two cohorts must be created before proceeding to Analyze Cohorts.'
        );
      } else {
        this.$emit('nextStep', true);
      }
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
    goto2p4() {
      if (this.filteredData.length < this.unfilteredData.length) {
        this.$emit('update:substep', '2.4');
      } else {
        this.displayErrorDialog(
          'No Cohort Filters Defined',
          'At least one filter must be added before continuing to the next step.'
        );
      }
    },
    goto2p5() {
      // TODO - check that collection was saved
      this.$emit('update:substep', '2.5');
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
