<template>
  <v-toolbar-items>
    <v-btn :disabled="!areVariablesSelected" flat @click="dialog = !dialog">
      <v-icon left>save</v-icon> SAVE DATASET
    </v-btn>
    <!-- SAVE COLLECTION FORM DIALOG -->
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-title primary-title>
          <span class="title pl-2">Save Dataset</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="onSaveCollection">
            <v-text-field
              v-model="collectionName"
              :rules="[
                () => !!collectionName || 'Collection name is required.',
              ]"
              prepend-inner-icon="table_chart"
              label="Please name your dataset."
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
          <v-btn @click="dialog = false">Cancel</v-btn>
          <v-btn
            :loading="loading"
            color="primary darken-4"
            @click="onSaveCollection"
          >
            <v-icon left>save</v-icon> Save</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-toolbar-items>
</template>

<script>
import { mapActions } from 'vuex';
import { actions } from '@/store/modules/datasetManager/types';

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
