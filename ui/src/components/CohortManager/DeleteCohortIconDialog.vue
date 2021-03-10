<template>
  <span>
    <v-icon :color="selected ? 'white' : ''" @click.stop="dialogClicked()"
      >delete</v-icon
    >

    <!-- DELETE COHORT FORM DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title color="white" primary-title>
          <v-icon color="primary">delete</v-icon>
          <span class="primary--text text--darken-3 title pl-2"
            >Delete Cohort</span
          >
        </v-card-title>

        <v-card-text class="primary primary--text text--lighten-5 pt-4">
          Are you sure you want to delete cohort<br />
          '{{ cohort.label }}'?
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn color="error" @click="onDeleteCohort">
            <v-icon left>delete</v-icon> Delete Cohort</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </span>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { actions, getters } from '@/store/modules/cohortManager/types';

// which store?
export default {
  props: {
    cohort: {
      type: Object,
      required: true,
    },
    selected: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    valid: true,
    dialog: false,
  }),
  computed: {},
  methods: {
    ...mapActions('cohortManager', {
      deleteCohort: actions.DELETE_COHORT,
    }),
    async onDeleteCohort() {
      try {
        await this.deleteCohort(this.cohort.id);
        this.$emit('cohortDeleted', true);
        this.dialog = false;
      } catch (err) {
        console.log('delete cohort failed, err=' + err);
      }
    },
    dialogClicked() {
      this.dialog = !this.dialog;
    },
  },
};
</script>

<style lang="scss" scoped></style>
