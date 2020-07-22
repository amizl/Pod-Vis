<template>
  <span>
    <v-tooltip top color="primary">
      <template v-slot:activator="{ on: tooltip }">
        <v-btn
          color="error"
          small
          v-on="{ ...tooltip }"
          @click="dialog = !dialog"
        >
          <v-icon color="white" left>delete</v-icon>DELETE
        </v-btn>
      </template>
      <span class="subtitle-1">Delete Study Dataset</span>
    </v-tooltip>

    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title primary-title>
          <span class="primary--text title pl-2"
            >Are you sure you want to delete this Study Dataset?</span
          >
        </v-card-title>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="red lighten-2" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn :loading="loading" color="primary" @click="onDeleteCollection">
            <v-icon color="" left>delete</v-icon> Delete Study Dataset</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </span>
</template>

<script>
import { mapActions } from 'vuex';
import { actions } from '@/store/modules/datasetManager/types';

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
    ...mapActions('datasetManager', {
      deleteCollection: actions.DELETE_COLLECTION,
    }),
    async onDeleteCollection() {
      try {
        await this.deleteCollection(this.collectionId);
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
