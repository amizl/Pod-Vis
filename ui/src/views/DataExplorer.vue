<template>
  <v-container v-if="isLoading" fluid fill-height class="ma-0 pa-1">
    <loading-spinner />
  </v-container>
  <v-container v-else fluid fill-height grid-list-mdt class="ma-0 pa-1">
    <v-toolbar app class="primary">
      <v-toolbar-title class="white--text">Data Explorer - {{ collection.label }}</v-toolbar-title>
    </v-toolbar>
    <v-layout column fill-height>
      <v-flex xs5 class="ma-0 pa-1">
        <v-layout fill-height>
          <v-flex xs12> <summary-view /> </v-flex>
        </v-layout>
      </v-flex>
      <v-flex xs7 class="ma-0 pa-1">
        <v-layout fill-height>
          <v-flex xs3 fill-height>
            <v-layout column fill-height>
              <v-flex fill-height class="ma-0 pa-1"> <cohorts /> </v-flex>
            </v-layout>
          </v-flex>
          <v-flex xs9 class="ma-0 pa-1"> <detailed-view /> </v-flex>
          <v-flex xs3 class="ma-0 pa-1">
            <v-layout column fill-height>
              <v-flex> <analytics /> </v-flex>
            </v-layout>
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/dataExplorer/types';
import SummaryView from '@/components/DataExplorer/SummaryView.vue';
import Cohorts from '@/components/DataExplorer/Cohorts.vue';
import Analytics from '@/components/DataExplorer/Analytics.vue';
import DetailedView from '@/components/DataExplorer/DetailedView.vue';

export default {
  components: {
    Analytics,
    SummaryView,
    Cohorts,
    DetailedView,
  },
  props: {
    collectionId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      cohorts: state.COHORTS,
      collection: state.COLLECTION,
      outcomeVariables: state.OUTCOME_VARIABLES,
    }),
  },
  async created() {
    // this.resetAllStoreData();
    this.isLoading = true;
    await this.fetchCohorts();
    await this.fetchCollection(this.collectionId);
    await this.fetchData();
    this.isLoading = false;

    // set outcome variables to union of cohorts' output variables
    var vars_added = {};
    var outcome_vars = [];
    this.cohorts.filter(v => v.collection_id == this.collectionId).forEach(function(c) {
	var output_vars = c.output_variables;
	output_vars.forEach(function(ov) {
	    var id = ov.observation_ontology.id;
	    if (!(id in vars_added)) {
		vars_added[id] = 1;
		outcome_vars.push(ov.observation_ontology);
	    }
	});
    });
    this.setOutcomeVariables(outcome_vars);
  },
  methods: {
    ...mapActions('dataExplorer', {
      fetchCohorts: actions.FETCH_COHORTS,
      fetchCollection: actions.FETCH_COLLECTION,
      fetchData: actions.FETCH_DATA,
      setOutcomeVariables: actions.SET_OUTCOME_VARIABLES,
   })
  },
};
</script>

<style scoped></style>
