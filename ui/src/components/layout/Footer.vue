<template lang="pug">
  v-footer(app dense dark).primary
    v-spacer
    //- img(src='./assets/gray-som-logo.svg')
    //- h3.pa-3 {{ title }} &copy; {{ copy }}
    v-spacer
</template>

<script>
export default {
  data() {
    return {
      title: 'UNIVERSITY OF MARYLAND BALTIMORE',
    };
  },
  computed: {
    copy() {
      return new Date().getFullYear();
    },
  },
};
</script>

<style></style>
