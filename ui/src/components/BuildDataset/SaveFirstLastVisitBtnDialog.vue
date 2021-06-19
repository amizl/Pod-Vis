<template>
  <div>
    <v-btn
      :disabled="disableButton"
      color="primary--text"
      @click="dialog = !dialog"
    >
      <v-icon left>save</v-icon> SAVE VISITS
    </v-btn>
    <!-- SAVE FIRST/LAST VISIT DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title color="white" primary-title>
          <v-icon color="primary darken-3">save</v-icon>
          <span class="primary--text text--darken-3 title pl-2"
            >Save First/Last Visits</span
          >
        </v-card-title>

        <v-card-text class="primary primary--text text--lighten-5 pt-4">
          <ul>
            <li v-for="(descr, index) in varDescriptions" :key="`vd-${index}`">
              {{ descr }}
            </li>
          </ul>
          <div class="pt-3">
            Study Population - {{ numSelectedSubjects }} subject(s)
          </div>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="dialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            @click="onSaveFirstLastVisit"
          >
            <v-icon left>save</v-icon> Save</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataSummary/types';
import { getObservationVariableIds } from '@/utils/helpers';

// which store?
export default {
  props: {
    useLongScaleNames: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    valid: true,
    dialog: false,
    loading: false,
  }),
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      firstVisits: state.FIRST_VISITS,
      lastVisits: state.LAST_VISITS,
      visitVariable: state.VISIT_VARIABLE,
      numSelectedSubjects: state.NUM_SELECTED_SUBJECTS,
    }),
    disableButton() {
      var disabled = false;
      if (this.numSelectedSubjects == 0) {
        disabled = true;
      } else {
        var cvIds = getObservationVariableIds(this.collection);
        var firstVisits = this.firstVisits;
        var lastVisits = this.lastVisits;
        cvIds.forEach(cvid => {
          if (
            !(cvid in firstVisits) ||
            firstVisits[cvid] == null ||
            !(cvid in lastVisits) ||
            lastVisits[cvid] == null
          ) {
            disabled = true;
          }
        });
      }
      return disabled;
    },
    varDescriptions() {
      var descrs = [];
      var cvIds = getObservationVariableIds(this.collection);
      var firstVisits = this.firstVisits;
      var lastVisits = this.lastVisits;
      var varIdToName = {};
      this.collection.observation_variables_list.forEach(ov => {
        if (this.useLongScaleNames) {
          varIdToName[ov['ontology']['id']] = ov['ontology']['label'];
        } else {
          varIdToName[ov['ontology']['id']] = ov['ontology']['abbreviation'];
        }
      });

      cvIds.forEach(cvid => {
        descrs.push(
          varIdToName[cvid] +
            ': ' +
            firstVisits[cvid] +
            ' - ' +
            lastVisits[cvid]
        );
      });
      return descrs;
    },
  },
  watch: {
    dialog() {
      this.$emit('dialogOpen', this.dialog);
    },
  },
  methods: {
    ...mapActions('dataSummary', {
      saveFirstAndLastVisits: actions.SAVE_FIRST_AND_LAST_VISITS,
    }),
    async saveVisits() {
      var variableVisits = [];
      var cvIds = getObservationVariableIds(this.collection);
      var firstVisits = this.firstVisits;
      var lastVisits = this.lastVisits;
      var vvar =
        this.visitVariable === 'Visit Event' ? 'visit_event' : 'visit_num';

      cvIds.forEach(cvid => {
        var fkey = 'first_' + vvar;
        var lkey = 'last_' + vvar;
        var vv = { variable_id: Number(cvid) };
        vv[fkey] = firstVisits[cvid];
        vv[lkey] = lastVisits[cvid];
        variableVisits.push(vv);
      });

      this.saveFirstAndLastVisits({
        variableVisits,
      });
    },
    async onSaveFirstLastVisit() {
      this.loading = true;
      this.saveVisits();
      this.loading = false;
      // move on to the cohort manager
      this.$router.push(`/cohorts?collection=${this.collection.id}`);
    },
  },
};
</script>

<style lang="scss" scoped></style>
