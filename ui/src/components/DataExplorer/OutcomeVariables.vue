<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-card-title class="title primary--text"> Outcome Variables </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <v-treeview
        v-model="selectedObservationVariables"
        color="primary"
        selectable
        return-object
        :items="observationVariables"
        item-text="label"
      ></v-treeview>
    </v-card-text>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';

export default {
  data() {
    return {
      selectedObservationVariables: [],
      observationVariables: [],
    };
  },
  computed: {
    ...mapState('dataExplorer', {
      collection: state.COLLECTION,
    }),
  },
  async created() {
    this.observationVariables = this.collection.observation_variables;
  },
};
</script>

<style scoped></style>
