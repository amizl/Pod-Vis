<template lang="pug">
  v-app
    app-header
    v-content
      router-view
</template>

<script>
import Header from './components/Header.vue';

export default {
  components: {
    appHeader: Header,
  },
  name: 'App',
  data() {
    return {
    };
  },
};
</script>

<style scoped>
.v-content {
  background-color: #f3f3f3;
}
</style>
