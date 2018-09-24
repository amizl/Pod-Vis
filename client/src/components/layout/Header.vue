<template lang='pug'>
  v-toolbar(
    fixed
    dense
  ).primary
    v-toolbar-title(left) Foo
    //-   v-spacer
    //-   v-btn(
    //-     flat v-for='item in menuItems'
    //-     :key='item.name'
    //-     :to='item.path'
    //-   )
    //-     v-icon(left) {{ item.icon }}
    //-     | {{ item.name }}
    //- v-spacer
    //- v-toolbar-items
    //-   v-btn(flat @click='signUserOut') Sign Out

</template>

<script>
export default {
  data() {
    return {
    };
  },
};
</script>

<style scoped>
</style>
