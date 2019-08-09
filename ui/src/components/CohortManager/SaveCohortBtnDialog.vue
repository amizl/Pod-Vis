<template>
  <div>
    <v-btn
      :disabled="!hasUserFilteredInputVariables"
      color="primary--text"
      @click="dialog = !dialog"
    >
      <v-icon left>save</v-icon> SAVE COHORT
    </v-btn>
    <!-- SAVE COLLECTION FORM DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <!-- <v-card max-height="500px" class="rounded-lg">
        <v-card-title class="title primary--text text--darken-3">
          Save Cohort
        </v-card-title>
        <v-sheet class="pa-3 background"> </v-sheet>
        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="onSaveCollection">
            <v-text-field
              v-model="collectionName"
              :rules="[
                () => !!collectionName || 'Collection name is required.',
              ]"
              prepend-inner-icon="table_chart"
              label="Please name your cohort."
              box
              flat
              background-color="grey lighten-4"
              class="mt-2"
              hide-details
            >
            </v-text-field>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" flat @click="dialog = false"
            ><v-icon left dark>close</v-icon>Close</v-btn
          >
        </v-card-actions>
      </v-card> -->
      <v-card class="rounded-lg">
        <v-card-title primary-title>
          <span class="primary--text title pl-2">Save Cohort</span>
        </v-card-title>
        <v-sheet class="pa-3 background"> </v-sheet>
        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="onSaveCollection">
            <v-text-field
              v-model="collectionName"
              :rules="[
                () => !!collectionName || 'Collection name is required.',
              ]"
              prepend-inner-icon="table_chart"
              label="Please name your cohort."
              box
              flat
              background-color="grey lighten-4"
              class="mt-2"
              hide-details
            >
            </v-text-field>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="red lighten-2" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn :loading="loading" color="primary" @click="onSaveCollection">
            <v-icon left>save</v-icon> Save Cohort</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { actions, getters } from '@/store/modules/cohortManager/types';

// which store?
export default {
  props: {
    variables: {
      type: Array,
      default: () => [],
    },
    datasetIds: {
      type: Array,
      default: () => [],
    },
  },
  data: () => ({
    collectionName: '',
    valid: true,
    dialog: false,
    loading: false,
  }),
  computed: {
    ...mapGetters('cohortManager', {
      hasUserFilteredInputVariables: getters.HAS_USER_FILTERED_INPUT_VARIABLES,
    }),
    areVariablesSelected() {
      return this.variables.length > 0;
    },
  },
  methods: {
    ...mapActions('datasetManager', {
      saveCollection: actions.SAVE_COLLECTION,
    }),
    async onSaveCollection() {
      const { collectionName, variables, datasetIds } = this;
      if (this.$refs.form.validate()) {
        this.loading = true;
        try {
          await this.saveCollection({ collectionName, variables, datasetIds });
          this.loading = false;
          this.$router.push('/datasets');
        } catch (err) {
          this.loading = false;
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
