<template>
  <v-container fluid grid-list-md>
    <v-toolbar app class="white">
      <v-toolbar-title>Cohort Manager</v-toolbar-title>
    </v-toolbar>
    <v-layout row>
      <v-flex xs3> <variable-tree /> </v-flex>
      <v-flex xs9>
        <v-layout row>
          <v-flex> <input-variables /> </v-flex>
        </v-layout>
        <v-layout row>
          <v-flex> <output-variables /> </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { actions, state } from '@/store/modules/cohortManager/types';

import InputVariables from '@/components/CohortManager/InputVariables.vue';
import OutputVariables from '@/components/CohortManager/OutputVariables.vue';
import VariableTree from '@/components/CohortManager/VariableTree.vue';

export default {
  name: 'CohortManager',
  components: {
    InputVariables,
    OutputVariables,
    VariableTree,
  },
  props: {
    collectionId: {
      type: Number,
      required: true,
    },
  },
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
    }),
  },
  created() {
    this.fetchCollection(this.collectionId);
  },
  methods: {
    ...mapActions('cohortManager', {
      fetchCollection: actions.FETCH_COLLECTION,
    }),
  },
};
</script>

<style scoped></style>
