<template>
  <v-dialog v-model="show" width="500">
    <v-card class="rounded-lg">
      <v-card-title color="white" primary-title>
        <v-icon color="primary darken-3">warning</v-icon>
        <span class="primary--text text--darken-3 title pl-2">{{
          confirmationTitle
        }}</span>
      </v-card-title>

      <v-card-text class="primary primary--text text--lighten-5 pt-4">
        {{ confirmationMessage }}
      </v-card-text>

      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text color="red lighten-2" @click="close()">
          <v-icon left>close</v-icon> Cancel
        </v-btn>
        <v-btn color="primary" @click="navigationConfirmed()"> OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    confirmationTitle: {
      type: String,
      required: false,
      default: 'Please Confirm',
    },
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
