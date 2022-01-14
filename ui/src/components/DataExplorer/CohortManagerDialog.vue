<template>
  <div>
    <v-tooltip top color="primary">
      <template v-slot:activator="{ on: tooltip }">
        <v-btn
          text
          color="primary"
          style="height:100%;"
          @click="dialog = !dialog"
          v-on="{ ...tooltip }"
        >
          <v-icon left dark>add_box</v-icon>
          Cohorts
        </v-btn>
      </template>
      <span>Launch Study Group Selector to add/remove Study Groups</span>
    </v-tooltip>

    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title class="title primary--text text--darken-3">
          <span class="primary--text title pl-2"
            >Are you sure you want to leave Data Analytics and go to the Study
            Group Selector?</span
          >
        </v-card-title>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="red lighten-2" @click="dialog = false">
            <v-icon left>close</v-icon> No
          </v-btn>
          <v-btn
            :loading="loading"
            color="primary"
            @click="launchCohortManager"
          >
            Yes</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
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
  computed: {},
  methods: {
    async launchCohortManager() {
      try {
        this.$router.push(`/cohorts?collection=${this.collectionId}`);
        this.loading = false;
        this.dialog = false;
      } catch (err) {
        this.loading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
