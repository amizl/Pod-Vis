<template>
  <div style="background: white">
    <v-stepper v-model="step" :value="step" alt-labels>
      <v-stepper-header>
        <v-stepper-step
          :complete="step > 1"
          step="1"
          :style="stepStyle('1')"
          :class="stepClass('1')"
          @click.native="gotoHomepage()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }"
                >Home Page</span
              >
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
          @click.native="gotoDatasetManager()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }"
                >Dataset Manager</span
              >
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
          @click.native="gotoCohortManager()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }"
                >Cohort Manager</span
              >
            </template>
            <span class="subtitle-1">{{ step_descr['3'] }}</span>
          </v-tooltip>
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="step > 4"
          step="4"
          :style="stepStyle('4')"
          :class="stepClass('4')"
          @click.native="gotoSummaryMatrix()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }"
                >Summary Matrix</span
              >
            </template>
            <span class="subtitle-1">{{ step_descr['4'] }}</span>
          </v-tooltip>
        </v-stepper-step>

        <v-divider></v-divider>

        <v-stepper-step
          :complete="step > 5"
          step="5"
          :style="stepStyle('5')"
          :class="stepClass('5')"
          @click.native="gotoDataExplorer()"
        >
          <v-tooltip color="primary" bottom>
            <template v-slot:activator="{ on: tooltip }">
              <span class="subtitle-1" align="center" v-on="{ ...tooltip }"
                >Data Explorer</span
              >
            </template>
            <span class="subtitle-1">{{ step_descr['5'] }}</span>
          </v-tooltip>
        </v-stepper-step>
      </v-stepper-header>

      <v-stepper-items> </v-stepper-items>
    </v-stepper>

    <!-- substep trackers -->
    <v-stepper v-if="step === '2'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step :complete="substep !== '2.1' || step === '3'" step="2.1"
          ><span class="subtitle-1">Choose Datasets</span>
          <span
            >Choose datasets and click "SELECT VARIABLES"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="substep === '2.3' || substep === '2.4' || step === '3'"
          step="2.2"
          ><span class="subtitle-1">Select Variables</span>
          <span
            >Select variables and click on "SAVE STUDY DATASET"</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="substep === '2.4' || step === '3'" step="2.3"
          ><span class="subtitle-1">Save Study Dataset</span></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="step === '3'" step="2.4"
          ><span class="subtitle-1"
            >Choose First & Last Visit</span
          ></v-stepper-step
        >
      </v-stepper-header>
    </v-stepper>

    <v-stepper v-if="step === '3'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step
          :complete="inputVariables.length > 0 || substep >= 3.4"
          step="3.1"
          ><span class="subtitle-1"
            >Choose Predictor Variables</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="outputVariables.length > 0 || substep >= 3.4"
          step="3.2"
          ><span class="subtitle-1"
            >Choose Outcome Variables</span
          ></v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step
          :complete="
            filteredData.length < unfilteredData.length || substep >= 3.4
          "
          step="3.3"
          >Apply Filters to Variables</v-stepper-step
        >
        <v-divider></v-divider>
        <v-stepper-step :complete="substep === '3.5'" step="3.4"
          ><span class="subtitle-1">Save Cohort</span></v-stepper-step
        >

        <v-divider></v-divider>
        <v-stepper-step step="3.5"
          ><span class="subtitle-1">Repeat or Continue</span></v-stepper-step
        >
      </v-stepper-header>
      <v-stepper-items>
        <v-stepper-content step="3.1">
          Click on "CHOOSE PREDICTOR VARIABLES" below and select one or more
          variables, then click here to
          <v-btn small outlined color="primary--text" @click="goto3p2()"
            >CONTINUE</v-btn
          >.
        </v-stepper-content>

        <v-stepper-content step="3.2">
          Click on "CHOOSE OUTCOME VARIABLES" below and select one or more
          variables, then click here to
          <v-btn small outlined color="primary--text" @click="goto3p3()"
            >Continue</v-btn
          >.
        </v-stepper-content>

        <v-stepper-content step="3.3">
          Apply filters to predictor variables to define the desired cohort,
          then click here to
          <v-btn small outlined color="primary--text" @click="goto3p4()"
            >Continue</v-btn
          >
          and/or use the "CREATE COMPARATOR COHORTS" buttons below to create and
          save multiple cohorts at once.
        </v-stepper-content>

        <v-stepper-content step="3.4">
          Click on "SAVE COHORT" in the toolbar above to name and save this
          cohort.
        </v-stepper-content>

        <v-stepper-content step="3.5">
          <div v-if="collection_cohorts.length < 3">
            So far only {{ collection_cohorts.length }}
            <span v-if="collection_cohorts.length === 1">cohort has</span>
            <span v-else>cohorts have</span> been defined. To proceed to the
            Summary Matrix a minimum of 3 distinct cohorts must be created and
            saved. Click on:<br clear="both" />
            <v-btn small outlined color="primary--text" @click="createSimilar()"
              >Create Similar Cohort</v-btn
            >
            to create another cohort based on the last one<br clear="both" />
            <v-btn small outlined color="primary--text" @click="createNew()"
              >Create New Cohort</v-btn
            >
            to create a new cohort from scratch.
          </div>
          <div v-else>
            {{ collection_cohorts.length }} cohorts have been created and saved.
            Click on:<br clear="both" />
            <v-btn small outlined color="primary--text" @click="createSimilar()"
              >Create Similar Cohort</v-btn
            >
            to create another cohort based on the last one<br clear="both" />
            <v-btn small outlined color="primary--text" @click="createNew()"
              >Create New Cohort</v-btn
            >
            to create a new cohort from scratch<br clear="both" />
            <v-btn
              small
              outlined
              color="primary--text"
              @click="gotoSummaryMatrix()"
              >Continue</v-btn
            >
            to proceed to the Summary Matrix.
          </div>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>

    <v-stepper v-if="step === '4'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step step="4.1">Choose cohorts to compare.</v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step step="4.2"
          >Select a variable from Analytics panel.</v-stepper-step
        >
      </v-stepper-header>

      <v-stepper-items>
        <v-stepper-content step="4.1">
          Choose two or more cohorts to include in the analysis, then click "Continue".
        </v-stepper-content>
        <v-stepper-content step="4.2">
          Select a variable from the Analytics panel to see the all-vs-all
          cohort comparison via the Tukey/Range HSD Test. Click on a cell in
          that table to compare the corresponding pair of cohorts in the Data
          Explorer.
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>

    <!--(top), then click on
          one of the p-values in the Tukey/Range HSD test table (bottom) to
          compare those cohorts in the Data Explorer. -->

    <v-stepper v-if="step === '5'" :value="substep" model="substep">
      <v-stepper-header class="tracker_step_highlight">
        <v-stepper-step step="5.1"
	 >Select the cohorts and scale (i.e., outcome variable) to display in the Detailed View
	  by using the Cohorts Included in Analysis table (top) and the Analytics panel (bottom left), respectively.
	  Use the checkboxes to control which cohorts appear in the Detailed View and click on the desired scale
	  in the Analytics panel.
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
        '1': 'Archive of Uploaded Datasets',
        '2': 'Create your study dataset',
        '3': 'Design your query: Choose predictors and outcomes',
        '4': 'Compare cohorts in the Summary Matrix.',
        '5': 'Examine cohorts and variables in the Data Explorer.',
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
        return 'tracker_step_highlight pb-2';
      } else {
        return 'pb-2';
      }
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
      if (this.step == 2) {
        // no-op
      } else if (this.step > 2) {
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
      if (this.step == 3) {
        // no-op
      } else if (this.step == 2 && this.substep == 2.4) {
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
      } else if (this.step <= 2) {
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
      if (this.step == 4) {
        // no-op
      } else if (this.step <= 2) {
        this.displayErrorDialog(
          'No Study Dataset',
          'A study dataset must be created before the Data Explorer can be used. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else {
        this.$router.push(`explore?collection=${this.collectionId}`);
      }
    },
    gotoSummaryMatrix() {
      if (this.step <= 2) {
        this.displayErrorDialog(
          'No Study Dataset',
          'A study dataset must be created before the Summary Matrix can be viewed. ' +
            "Please either create a new study dataset first, or return to the home page and use the 'Add Cohorts' " +
            'link for an existing study dataset.'
        );
      } else {
        this.$router.push(`summary?collection=${this.collectionId}`);
      }
    },
    // Cohort Manager sub-step transitions.
    goto3p1() {
      this.$emit('update:substep', '3.1');
    },
    createNew() {
      this.$emit('createNew', true);
    },
    createSimilar() {
      this.$emit('createSimilar', true);
    },
    goto3p2() {
      if (this.inputVariables.length > 0) {
        this.$emit('update:substep', '3.2');
      } else {
        this.displayErrorDialog(
          'No Predictor Variables',
          'At least one predictor variable must be selected before continuing to the next step.'
        );
      }
    },
    goto3p3() {
      if (this.outputVariables.length > 0) {
        this.$emit('update:substep', '3.3');
      } else {
        this.displayErrorDialog(
          'No Outcome Variables',
          'At least one outcome variable must be selected before continuing to the next step.'
        );
      }
    },
    goto3p4() {
      if (this.filteredData.length < this.unfilteredData.length) {
        this.$emit('update:substep', '3.4');
      } else {
        this.displayErrorDialog(
          'No Cohort Filters Defined',
          'At least one filter must be added before continuing to the next step.'
        );
      }
    },
    goto3p5() {
      // TODO - check that collection was saved
      this.$emit('update:substep', '3.5');
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
