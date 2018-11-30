c<template lang='pug'>
  v-layout(
    align-center
    justify-center
    fill-height
  )
    half-circle-spinner(
      :animation-duration="1000"
      :size="size"
      :color='color'
    )
</template>

<script>
import { HalfCircleSpinner } from 'epic-spinners';

const SMALL = 25;
const MEDIUM = 75;
const LARGE = 125;

export default {
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
  components: {
    HalfCircleSpinner,
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

<style scoped>
</style>
