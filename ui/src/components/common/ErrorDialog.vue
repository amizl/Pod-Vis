<template>
  <v-dialog v-model="show" width="500">
    <v-card class="rounded-lg">
      <v-card-title class="title primary--text text--darken-3">
        <span class="primary--text title pl-2">{{ errorMessage }} </span>
      </v-card-title>
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
