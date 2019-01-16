<template>
  <v-container fluid fill-height>
    <v-toolbar app flat color="background">
      <p class="subheading foo--text mt-3">
        You are building a cohort for
        <span class="font-weight-bold"> {{ name }}</span>
      </p>
      <v-spacer></v-spacer>
      <v-btn flat color="primary">
        <v-icon left="">save</v-icon>
        Save Cohort
      </v-btn>
    </v-toolbar>
    <v-layout justify-space-around wrap>
      <!-- <v-progress-circular
        v-if="loading"
        indeterminate
        color="secondary"
        size="100"
        width="10"
      ></v-progress-circular> -->
      <v-flex xs12> </v-flex>
      <v-flex xs12>
        <v-card class="ui-card">
          <parallel-coordinates></parallel-coordinates>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import { actions, getters, state } from '@/store/modules/cohort/types';
import CohortCard from '@/components/CohortManager/CohortCard.vue';
import ParallelCoordinates from '@/components/charts/ParallelCoordinates.vue';
import ContentHeader from '../components/layout/Header.vue';
import * as firebase from 'firebase';

export default {
  components: {
    CohortCard,
    ContentHeader,
    ParallelCoordinates,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {};
  },
  computed: {
    ...mapGetters('cohort', {
      name: getters.GET_DATASET_NAME,
    }),
    // loading() {
    //   return Object.keys(this.dataset) == 0;
    // },
  },
  async created() {
    await this.fetchDataset(this.id);
    // const dataset = await this.fetchDataset(this.id);
    // if (dataset.exists) {
    //   this.dataset = dataset.data();
    // }
  },
  methods: {
    ...mapActions('cohort', {
      fetchDataset: actions.FETCH_DATASET,
    }),
  },
};
</script>

<style scoped></style>
