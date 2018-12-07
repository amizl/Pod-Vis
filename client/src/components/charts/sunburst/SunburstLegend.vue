<template>
  <v-treeview
    activatable
    open-on-click
    transition
    :items='items'
    item-key='name'
  >
  </v-treeview>
</template>

<script>
  export default {
    props: {
      items: Array,
    }
  }
</script>

<style scoped>

</style>