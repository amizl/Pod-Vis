<template>
  <div class="ma-0">
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              >Choose Outcome Variable
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-container fluid fill-height class="pa-0 pl-3 pt-3 ma-1">
      <span>Variable:</span>
      <v-btn-toggle v-model="dview" class="pl-2" mandatory>
        <v-btn
          v-for="v in outcomeVariables"
          text
          color="primary"
          class="white--text"
          :value="v"
          >{{ v.label }}</v-btn
        >
      </v-btn-toggle>
    </v-container>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/dataExplorer/types';

export default {
  components: {},
  data() {
    return {
      dview: null,
    };
  },
  watch: {
    dview(newval) {
      this.setDetailedView(newval);
    },
  },
  mounted() {
    if (this.detailedView == null) {
      if (this.dview != null) {
        this.setDetailedView(this.dview);
      }
    } else {
      this.dview = this.detailedView;
    }
  },
  computed: {
    ...mapState('dataExplorer', {
      detailedView: state.DETAILED_VIEW,
      outcomeVariables: state.OUTCOME_VARIABLES,
      collection: state.COLLECTION,
    }),
    userAddedOutcomeVariables() {
      return this.outcomeVariables.length > 0;
    },
  },
  methods: {
    ...mapActions('dataExplorer', {
      setDetailedView: actions.SET_DETAILED_VIEW,
    }),
  },
};
</script>

<style scoped></style>
