<template>
  <div>
    <v-btn
      :disabled="
        numSubjectsSelected === 0 ||
          numSubjectVarsSelected + numObservationVarsSelected === 0 ||
          (automatedAnalysisMode &&
            (automatedAnalysisPredictorVars.length == 0 ||
              automatedAnalysisOutputVars.length == 0))
      "
      color="primary--text"
      @click="dialog = !dialog"
    >
      <v-icon left>save</v-icon
      ><span v-if="!automatedAnalysisMode">SAVE STUDY DATASET</span
      ><span v-else>BEGIN ANALYSIS</span>
    </v-btn>
    <!-- SAVE COLLECTION FORM DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title color="white" primary-title>
          <v-icon color="primary">save</v-icon>
          <span class="primary--text text--darken-3 title pl-2"
            >Save Study Dataset</span
          >
        </v-card-title>

        <v-card-text class="primary primary--text text--lighten-5 pt-4">
          <v-form
            ref="form"
            v-model="valid"
            class="white"
            @submit.prevent="onSaveCollection"
          >
            <v-text-field
              ref="vtf"
              v-model="collectionName"
              :rules="[
                () => !!collectionName || 'Study Dataset name is required.',
              ]"
              prepend-inner-icon="table_chart"
              label="Please name your study dataset."
              filled
              text
              background-color="grey lighten-4"
              class="mt-2"
            >
            </v-text-field>
          </v-form>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn :loading="loading" color="primary" @click="onSaveCollection">
            <v-icon left>save</v-icon> Save Dataset</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import { actions } from '@/store/modules/datasetManager/types';

export default {
  props: {
    variables: {
      type: Array,
      default: () => [],
    },
    datasetIds: {
      type: Array,
      default: () => [],
    },
    numSubjectsSelected: {
      type: Number,
      default: 0,
    },
    numObservationVarsSelected: {
      type: Number,
      default: 0,
    },
    numSubjectVarsSelected: {
      type: Number,
      default: 0,
    },
    automatedAnalysisMode: {
      type: Boolean,
      default: false,
    },
    automatedAnalysisPredictorVars: {
      type: Array,
      default: () => [],
    },
    automatedAnalysisOutputVars: {
      type: Array,
      default: () => [],
    },
  },
  data: () => ({
    collectionName: '',
    valid: true,
    dialog: false,
    loading: false,
  }),
  computed: {
    areVariablesSelected() {
      return this.variables.length > 0;
    },
  },
  watch: {
    dialog(val) {
      if (val) {
        this.showing();
        this.$emit('dialogOpen', this.dialog);
      }
    },
  },
  methods: {
    ...mapActions('datasetManager', {
      saveCollection: actions.SAVE_COLLECTION,
    }),
    showing() {
      setTimeout(() => {
        this.$refs.vtf.focus();
      });
    },
    async onSaveCollection() {
      const { collectionName, variables, datasetIds } = this;
      if (this.$refs.form.validate()) {
        this.loading = true;
        try {
          const newCollection = await this.saveCollection({
            collectionName,
            variables,
            datasetIds,
          });
          this.$emit('collectionSaved');
          this.loading = false;
          var query = { collection: newCollection.id };
          if (this.automatedAnalysisMode) {
            query['aa_predictors'] = this.automatedAnalysisPredictorVars.map(
              v => v.id
            );
            query['aa_outputs'] = this.automatedAnalysisOutputVars.map(
              v => v.id
            );
            // encode predictor prefs
            // e.g., aaRanges=quartiles|22,23||tertiles|17,18 - ranges
            // aaMCS=1|22,23||5|17,18 - min category sizes
            // aaWhichOutcomes=firstVisit|9,10||ROC|11,12
            const d1 = '|';
            const d2 = '||';
            var pph = {};
            this.automatedAnalysisPredictorVars.map(v => {
              var key = null;
              if ('aaRanges' in v) {
                key = v.aaRanges;
              } else if ('aaMinCatSize' in v) {
                key = v.aaMinCatSize;
              }
              if ('aaWhichOutcome' in v) {
                key = v.aaWhichOutcome;
              }
              if (!(key in pph)) {
                pph[key] = [];
              }
              pph[key].push(v.id);
            });
            query['aa_ranges'] = ['quartiles', 'tertiles', 'halves']
              .filter(r => r in pph)
              .map(r => {
                return r + d1 + pph[r].join(',');
              })
              .join(d2);
            query['aa_mcs'] = [1, 5, 10, 20, 50]
              .filter(r => r in pph)
              .map(r => {
                return r + d1 + pph[r].join(',');
              })
              .join(d2);
            query['aa_which_outcomes'] = ['firstVisit', 'lastVisit', 'change', 'ROC']
              .filter(r => r in pph)
              .map(r => {
                return r + d1 + pph[r].join(',');
              })
              .join(d2);
          }
          this.$router.push({ name: 'dataSummary', query: query });
        } catch (err) {
          //          console.log('caught error ' + err);
          this.loading = false;
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
