<template lang='pug'>
  v-toolbar(app dense color='white')
    v-toolbar-title(left v-text='title')
    v-spacer
    v-toolbar-items
      v-btn(
        flat v-for='item in menuItems'
        :key='item.name'
        :to='item.path'
      )
        v-icon(left) {{ item.icon }}
        | {{ item.name }}
    v-spacer
    v-btn(flat @click='signUserOut') Sign Out

</template>

<script>

export default {
  data() {
    return {
      title: 'CliO-Vis',
      menuItems: [
        {
          name: 'COHORT MANAGER',
          icon: 'group',
          path: '/cohortManager',
        },
        {
          name: 'DATA EXPLORER',
          icon: 'explore',
          path: '/dataExplorer',
        },
        {
          name: 'ANALYSIS TOOL',
          icon: 'bar_chart',
          path: '/analysisTool',
        },
        {
          name: 'DATASET MANAGER',
          icon: 'table_chart',
          path: '/datasetManager',
        },
      ],
    };
  },
  methods: {
    signUserOut() {
      this.$store.dispatch('signUserOut');
    }
  }
};
</script>

<style scoped>
</style>

