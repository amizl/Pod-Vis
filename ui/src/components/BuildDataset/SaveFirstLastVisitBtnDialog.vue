<template>
  <div>
    <v-btn
      :disabled="!firstVisit || !lastVisit || numSelectedSubjects == 0"
      color="primary--text"
      @click="dialog = !dialog"
    >
      <v-icon left>save</v-icon> SAVE FIRST/LAST VISIT
    </v-btn>
    <!-- SAVE FIRST/LAST VISIT DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title primary-title>
          <span class="title pl-2">Save First and Last Visit</span>
        </v-card-title>
        <v-card-text class="title primary--text text--darken-3">
          <div class="primary--text title pl-2">
            <ul>
              <li>First Visit={{ firstVisit }}</li>
              <li>Last Visit={{ lastVisit }}</li>
              <li>Study Population={{ numSelectedSubjects }} subject(s)</li>
            </ul>
          </div>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="dialog = false">Cancel</v-btn>
          <v-btn
            :loading="loading"
            color="primary darken-4"
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
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      firstVisit: state.FIRST_VISIT,
      lastVisit: state.LAST_VISIT,
      visitVariable: state.VISIT_VARIABLE,
      numSelectedSubjects: state.NUM_SELECTED_SUBJECTS,
    }),
  },
  data: () => ({
    valid: true,
    dialog: false,
    loading: false,
  }),
  watch: {
    dialog() {
      this.$emit('dialogOpen', this.dialog);
    },
  },
  methods: {
    ...mapActions('dataSummary', {
      saveFirstAndLastVisits: actions.SAVE_FIRST_AND_LAST_VISITS,
    }),
    async onSaveFirstLastVisit() {
      //      const { collectionName, variables, datasetIds } = this;
      this.loading = true;

      var variableVisits = [];
      var cvIds = getObservationVariableIds(this.collection);
      var firstVisit = this.firstVisit;
      var lastVisit = this.lastVisit;
      var vvar =
        this.visitVariable === 'Visit Event' ? 'visit_event' : 'visit_num';

      cvIds.forEach(cvid => {
        var fkey = 'first_' + vvar;
        var lkey = 'last_' + vvar;
        var vv = { variable_id: Number(cvid) };
        vv[fkey] = firstVisit;
        vv[lkey] = lastVisit;
        variableVisits.push(vv);
      });

      try {
        this.saveFirstAndLastVisits({
          variableVisits,
        });

        this.loading = false;
        // move on to the cohort manager
        this.$router.push(`/cohorts?collection=${this.collection.id}`);
      } catch (err) {
        this.loading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
