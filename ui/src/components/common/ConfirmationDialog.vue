<template>
  <v-dialog v-model="show" width="500">
    <v-card class="rounded-lg">
      <v-card-title class="title primary--text text--darken-3">
        <span class="primary--text title pl-2">{{ confirmationMessage }} </span>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn flat color="red lighten-2" @click="close()">
          <v-icon left>close</v-icon> No
        </v-btn>
        <v-btn color="primary" @click="navigationConfirmed()"> Yes</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    confirmationMessage: {
      type: String,
      required: true,
    },
    show: {
      type: Boolean,
      required: true,
    },
    targetUri: {
      type: String,
      required: true,
    },
  },
  methods: {
    navigationConfirmed() {
      this.close();
      this.$router.push(this.targetUri);
    },
    close() {
      this.$emit('closed');
    },
  },
};
</script>

<style lang="scss" scoped></style>
