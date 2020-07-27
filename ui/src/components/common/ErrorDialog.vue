<template>
  <v-dialog v-model="show" width="500">
    <v-card class="rounded-lg">
      <v-card-title color="white" primary-title>
        <v-icon color="primary darken-3">warning</v-icon>
        <span class="primary--text text--darken-3 title pl-2">{{
          errorTitle
        }}</span>
      </v-card-title>

      <v-card-text class="primary primary--text text--lighten-5 pt-4">
        {{ errorMessage }}
      </v-card-text>

      <v-divider></v-divider>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="close()"> OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    errorTitle: {
      type: String,
      required: true,
    },
    errorMessage: {
      type: String,
      required: true,
    },
    show: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    close() {
      this.$emit('closed');
    },
  },
};
</script>

<style lang="scss" scoped></style>
