<template>
  <div>
    <v-tooltip bottom color="primary">
      <template v-slot:activator="{ on: tooltip }">
        <v-btn
          class="primary--text ma-0 px-2 py-0"
          :disabled="collection_cohorts.length < 2"
          @click="dialog = !dialog"
          v-on="{ ...tooltip }"
        >
          Data Analytics
        </v-btn>
      </template>
      <span>Leave the Study Group Selector and proceed to Data Analytics.</span>
    </v-tooltip>

    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title color="white" primary-title>
          <v-icon x-large color="primary">analytics</v-icon>
          <span class="primary--text text--darken-3 title pl-2"
            >Proceed to Data Analytics?</span
          >
        </v-card-title>

        <v-card-text class="primary primary--text text--lighten-5 pt-4">
          {{ collection_cohorts.length }} cohort{{
            collection_cohorts.length == 1 ? '' : 's'
          }}
          created. Click "OK" to proceed to Data Analytics to compare study
          groups OR "CANCEL" to continue creating study groups.
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn
            :loading="loading"
            color="primary"
            @click="routeToDataExplorer"
          >
            OK</v-btn
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
    routeToDataExplorer() {
      this.$router.push(`explore?collection=${this.collectionId}`);
    },
  },
};
</script>

<style lang="scss" scoped></style>
