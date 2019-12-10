<template>
  <div>
    <v-tooltip bottom color="primary">
      <template v-slot:activator="{ on }">
        <v-btn
          color="primary--text"
          :disabled="false"
          @click="dialog = !dialog"
          v-on="on"
        >
          <v-icon left>bar_chart</v-icon>
          Analyze
        </v-btn>
      </template>
      <span>View Analysis Summary for all Cohorts and Outcome Variables</span>
    </v-tooltip>

    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title class="title primary--text text--darken-3">
          <span class="primary--text title pl-2"
            >Are you sure you want to leave the Data Explorer and go to the
            Analysis Summary?</span
          >
        </v-card-title>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="red lighten-2" @click="dialog = false">
            <v-icon left>close</v-icon> No
          </v-btn>
          <v-btn
            :loading="loading"
            color="primary"
            @click="routeToAnalysisSummary"
          >
            Yes</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';

export default {
  props: {
    collectionId: {
      type: Number,
      required: true,
    },
  },
  data: () => ({
    dialog: false,
    loading: false,
  }),
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      cohorts: state.COHORTS,
    }),
    collection_cohorts() {
      const cch = [];
      const th = this;
      this.cohorts.forEach(e => {
        if (e.collection_id === th.collection.id) {
          cch.push(e);
        }
      });
      return cch;
    },
  },
  methods: {
    routeToAnalysisSummary() {
      this.$router.push(`summary?collection=${this.collectionId}`);
    },
  },
};
</script>

<style lang="scss" scoped></style>
