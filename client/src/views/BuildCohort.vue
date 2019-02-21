<template>
  <v-container fluid>
    <v-toolbar class="background" flat app>
      <v-spacer></v-spacer>
      <!-- <v-btn flat color="primary">
        <v-icon left="">save</v-icon>
        Save Cohort
      </v-btn> -->
    </v-toolbar>
    <v-layout justify-center>
      <v-flex xs10>
        <p class="subheading foo--text mt-3">
          You are building a cohort from
          <span class="font-weight-bold"> {{ name }}</span>
        </p>
        <v-divider></v-divider>
      </v-flex>
    </v-layout>
    <!-- <v-layout class="pt-2" justify-center>
      <v-flex xs10>
        <v-select
          :items="[{ name: 'Gender' }]"
          v-model="e11"
          chips
          label="Select Dimensions"
          item-text="name"
          item-value="name"
          max-height="auto"
          autocomplete
          multiple
          solo
          flat
        >
        </v-select>
        <v-btn flat>
          <v-icon left>format_color_fill</v-icon>
          Color</v-btn
        >
        <v-switch v-model="hideTicks" label="HIDE TICKS"></v-switch>
      </v-flex>
    </v-layout> -->
    <v-layout class="pt-5" justify-space-around wrap>
      <!-- <v-progress-circular
        v-if="loading"
        indeterminate
        color="secondary"
        size="100"
        width="10"
      ></v-progress-circular> -->
      <v-flex xs10>
        <v-card class="ui-card">
          <parallel-coordinates :ticks="!hideTicks"></parallel-coordinates>
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
    return {
      hideTicks: false,
      e11: [],
    };
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
