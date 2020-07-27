<template>
 <v-container fluid fill-width>
  <v-row>
   <v-col cols="12" align="center" justify="center">
    <v-progress-circular indeterminate :size='size' color='primary' />
   </v-col>
  </v-row>
 </v-container>
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
