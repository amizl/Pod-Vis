<template lang="pug">
  v-layout(
    align-center
    justify-center
    fill-height
  )
    v-progress-circular(
      indeterminate
      :size='size'
      color="primary"
    )
</template>

<script>
const SMALL = 25;
const MEDIUM = 50;
const LARGE = 125;

export default {
  name: 'LoadingSpinner',
  props: {
    small: {
      type: Boolean,
      default: false,
    },
    medium: {
      type: Boolean,
      default: false,
    },
    large: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    color() {
      return this.$vuetify.theme.primary;
    },
    size() {
      if (this.small) {
        return SMALL;
      } else if (this.medium) {
        return MEDIUM;
      } else if (this.large) {
        return LARGE;
      }

      return MEDIUM; // default
    },
  },
};
</script>

<style scoped></style>
