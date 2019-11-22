<template>
  <span>

   <v-tooltip top color="primary">
   <template v-slot:activator="{ on }">
   <v-btn
      flat
      color="error"
      v-on="on"
      @click="dialog = !dialog"
    >
      <v-icon color="error" left>delete</v-icon>DELETE
    </v-btn>
   </template>
   <span>Delete Collection</span>
   </v-tooltip>

    <v-dialog v-model="dialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title primary-title>
          <span class="primary--text title pl-2"
            >Are you sure you want to delete this Collection?</span
          >
        </v-card-title>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn flat color="red lighten-2" @click="dialog = false">
            <v-icon left>close</v-icon> Cancel
          </v-btn>
          <v-btn :loading="loading" color="primary" @click="onDeleteCollection">
            <v-icon color="" left>delete</v-icon> Delete Collection</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </span>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { actions, getters } from '@/store/modules/datasetManager/types';

export default {
  props: {
    collection_id: {
      type: Number,
      required: true,
    },
  },
  data: () => ({
    dialog: false,
    loading: false,
  }),
  computed: {
  },
  methods: {
    ...mapActions('datasetManager', {
      deleteCollection: actions.DELETE_COLLECTION,
    }),
    async onDeleteCollection() {
      try {
        await this.deleteCollection(this.collection_id);
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
